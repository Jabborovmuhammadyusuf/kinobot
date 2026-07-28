from aiogram.fsm.state import State, StatesGroup


class UploadState(StatesGroup):
    waiting_videos = State()
    waiting_code = State()
    waiting_name = State()
    waiting_status = State()       # faqat serial: belgilangan son / davom etmoqda
    waiting_parts_count = State()  # faqat serial: nechta qism/fasl
    waiting_description = State()


class AddEpisodeState(StatesGroup):
    waiting_code = State()
    waiting_videos = State()


class EditState(StatesGroup):
    waiting_code = State()
    waiting_field_choice = State()
    waiting_new_value = State()


class ChannelState(StatesGroup):
    waiting_channel = State()
    waiting_remove_choice = State()


class SearchState(StatesGroup):
    waiting_query = State()


class BroadcastState(StatesGroup):
    waiting_message = State()
