import reflex as rx
from reflex_local_auth import (
    LocalAuthState, LocalUser, require_login
)
from reflex_local_auth.pages import login_page, register_page
from sqlmodel import Field, Relationship

class ProtectedItem(rx.Model, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
    owner_id: int = Field(foreign_key="localuser.id")
    # Remove back_populates since LocalUser doesn't define items relationship

class DashboardState(LocalAuthState):
    new_text: str = ""

    @rx.var
    def user_items(self) -> list[ProtectedItem]:
        with rx.session() as s:
            return s.exec(
                ProtectedItem.select().where(
                    ProtectedItem.owner_id == self.authenticated_user.id
                )
            ).all()

    def add_item(self):
        if not self.new_text.strip():
            return
        with rx.session() as s:
            s.add(ProtectedItem(text=self.new_text, owner_id=self.authenticated_user.id))
            s.commit()
        self.new_text = ""

@require_login
def dashboard():
    return rx.center(
        rx.vstack(
            rx.heading("Welcome, ", DashboardState.authenticated_user.username),
            rx.input(
                placeholder="Save something…",
                value=DashboardState.new_text,
                on_change=DashboardState.set_new_text,
            ),
            rx.button("Save", on_click=DashboardState.add_item),
            rx.foreach(DashboardState.user_items, lambda i: rx.text(i.text)),
            rx.link("Logout", href="/logout"),
            spacing="4",
        ),
        height="100vh",
    )

app = rx.App()
app.add_page(login_page, route="/login")
app.add_page(register_page, route="/register")
app.add_page(dashboard, route="/")