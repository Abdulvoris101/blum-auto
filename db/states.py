from aiogram.fsm.state import StatesGroup, Stateclass AddAccountState(StatesGroup):    phoneNumber = State()    verificationCode = State()    password = State()class AccountSelectionState(StatesGroup):    accountName = State()class UserRegisterState(StatesGroup):    language = State()class AvailablePlayPassState(StatesGroup):    availablePlayPass = State()class PopupBalanceState(StatesGroup):    amount = State()