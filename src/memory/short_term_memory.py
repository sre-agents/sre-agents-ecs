from google.adk.sessions import InMemorySessionService

app_name_suffix = "_app"
user_id_suffix = "_user"
session_id_suffix = "_session"


class ShortTermMemory:
    def __init__(
        self,
        name: str = "short_term_memory",
    ):
        self.name = name

        self.app_name = name + app_name_suffix
        self.user_id = name + user_id_suffix
        self.session_id = name + session_id_suffix

        self.session_service = InMemorySessionService()

    @classmethod
    async def create(
        cls,
        name: str = "short_term_memory",
    ):
        # re-use google adk initialization
        app_name = name + app_name_suffix
        user_id = name + user_id_suffix
        session_id = name + session_id_suffix
        instance = cls(name=name)
        await instance.session_service.create_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        return instance
