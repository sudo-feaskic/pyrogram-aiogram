from aiogram.exceptions import TelegramBadRequest
from pyrogram import Client
from misc import env
from aiogram.fsm.context import FSMContext
from manager.m import dp, db
from aiogram.fsm.state import State, StatesGroup


class regUser(StatesGroup):
    phone_number = State()
    app_id = State()
    app_hash = State()
    type_number = State()
    otp_send = State()
    check_otp = State()
    _2fa = State()





@dp.message(F.text, regUser.app_id)
async def get_app_id(msg: types.Message, state: FSMContext):
    if msg.text:
        global api_id
        info.insert_app_id(msg.text)
        await msg.answer('APP HASH ni kiriting')
        api_id = msg.text
        await state.set_state(regUser.app_hash)

@dp.message(F.text, regUser.app_hash)
async def get_app_id(msg: types.Message, state: FSMContext):
    if msg.text:
        info.insert_app_hash(msg.text)
        await msg.answer('Nomeringizni kiriting')
        await state.set_state(regUser.otp_send)



@dp.message(regUser.otp_send)
async def otp(message: types.Message, state: FSMContext, bot: Bot):
  global client
  api_hash = env.api_hash
  app_id = env.api_id
  client = Client(f"userbot/userbot", app_id, api_hash)
  await client.connect()
  global phone_number
  phone_number = message.text
  info.insert_phonenumber(phone_number)
  global sent_code_info
  try:
    sent_code_info = await client.send_code(phone_number)
  except (PhoneNumberInvalid):
    await message.answer('Not\'g\'ri nomer kiritildi\n\n Misol: `+123456789`', parse_mode='MARKDOWN')
    return
  except Exception as e:
    await message.answer('Some 🤬🤬🤬 error')
    print(e)
    await message.answer(e)

  global phone_code
  await message.answer("Kodni shunaqa formatda kiriting:  `1/2/3/4/5`.", parse_mode='MARKDOWN')
  await state.set_state(regUser.check_otp)

@dp.message(regUser.check_otp)
async def otp(message: types.Message, state: FSMContext, bot: Bot):
  phone_code = re.sub(r'\D', '', message.text)
  try:
    await client.sign_in(phone_number, sent_code_info.phone_code_hash, phone_code)
    await message.answer('Tizimga kirildi')
    dialogs = client.get_dialogs()
    async for dialog in dialogs:
        print(f"Name: {dialog.chat.title or dialog.chat.first_name}")
        print(f"ID: {dialog.chat.id}")
        print(f"Type: {dialog.chat.type}")
        print("-----")
    await client.storage.save()
    await client.disconnect()
    await state.clear()
  
  except(SessionPasswordNeeded):
    await message.answer('2FA kodini kiriting:')
    await state.set_state(regUser._2fa)
  except Exception as e:
    print(e)

@dp.message(regUser._2fa)
async def otp(message: types.Message, state: FSMContext, bot: Bot):
  f2_code = message.text
  try:
    await client.check_password(f2_code)
    await client.send_message('me', await client.export_session_string())
    await message.answer('Successfully logined!')
    dialogs = client.get_dialogs()
    async for dialog in dialogs:
        print(f"Name: {dialog.chat.title or dialog.chat.first_name}")
        print(f"ID: {dialog.chat.id}")
        print(f"Type: {dialog.chat.type}")
        print("-----")
    await client.storage.save()
    await client.disconnect()
    await state.clear()
    print('Success')
  except(PasswordHashInvalid):
    await message.answer('Invalid 2FA password, try again')
