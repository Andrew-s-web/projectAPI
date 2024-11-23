from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from fastapi import HTTPException


app = FastAPI()

# Шаблоны
templates = Jinja2Templates(directory="templates")

# Статические файлы (если нужно CSS или изображения)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Хранилище для тикетов
tickets = []
ticket_id_counter = 1


# Главная страница: список тикетов с возможностью фильтрации
@app.get("/")
async def read_tickets(request: Request, title: Optional[str] = None, priority: Optional[str] = None):
    filtered_tickets = (

        [ticket for ticket in tickets if title.lower() in ticket["title"].lower()]
        if title
        else tickets
    )
    if priority:
        filtered_tickets = [ticket for ticket in tickets if ticket["priority"] == priority]
    return templates.TemplateResponse(
        "index.html", {"request": request, "tickets": filtered_tickets}
    )


# Страница формы для добавления/редактирования тикета
@app.get("/tickets/new")
async def new_ticket_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "ticket": None})


@app.post("/tickets")
async def create_ticket(
    title: str = Form(...), description: str = Form(...), priority: str = Form(...)
):
    global ticket_id_counter
    tickets.append({"id": ticket_id_counter, "title": title, "description": description, "priority": priority})
    ticket_id_counter += 1
    return RedirectResponse("/", status_code=303)


# Удаление тикета
@app.get("/tickets/delete/{ticket_id}")
async def delete_ticket(ticket_id: int):
    global tickets
    tickets = [ticket for ticket in tickets if ticket["id"] != ticket_id]
    return RedirectResponse("/", status_code=303)

@app.get("/tickets/edit/{ticket_id}")
async def edit_ticket_form(request: Request, ticket_id: int):
    # Найти тикет по ID
    ticket = next((ticket for ticket in tickets if ticket["id"] == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Передать тикет в шаблон формы
    return templates.TemplateResponse("edit.html", {"request": request, "ticket": ticket})


@app.patch("/tickets/edit/{ticket_id}")
async def update_ticket(
    ticket_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    priority: Optional[str] = Form(None)
):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            if title:
                ticket["title"] = title
            if description:
                ticket["description"] = description
            if priority:
                ticket["priority"] = priority
            return RedirectResponse("/", status_code=303)

    raise HTTPException(status_code=404, detail="Ticket not found")



@app.post("/tickets/edit/{ticket_id}")
async def edit_ticket(ticket_id: int, title: str = Form(None), description: str = Form(None), priority: str = Form(None)):
    return await update_ticket(ticket_id, title=title, description=description, priority=priority)

