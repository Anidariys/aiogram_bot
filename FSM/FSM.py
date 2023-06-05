from aiogram.filters.state import State, StatesGroup


class FSMNPForm(StatesGroup):
    NP_name = State()
    NP_city = State()
    NP_department = State()
    NP_phone = State()


class FSMDeliveryForm(StatesGroup):
    delivery_name = State()
    delivery_address = State()
    delivery_other = State()
    delivery_phone = State()
    delivery_comment = State()
    delivery_photo = State()
    delivery_location = State()


class FSMBussForm(StatesGroup):
    buss_name = State()
    buss_city = State()
    buss_phone = State()


class FSMUpdateForm(StatesGroup):
    set_group = State()
    set_name = State()
    set_kay = State()
    set_value = State()
    set_photo = State()
    set_location = State()
    set_phone = State()


class FSMGetClientData(StatesGroup):
    get_group = State()
    get_name = State()


class FSMDeletClient(StatesGroup):
    get_group = State()
    get_name = State()


class FSMAdminChoice(StatesGroup):
    choice = State()


class FSMAdmindDeleteUser(StatesGroup):
    delete = State()

class FSMUserReg(StatesGroup):
    reg = State()

