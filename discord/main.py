import asyncio

from interactions import listen, Button, Client, Intents, slash_command, SlashContext, spread_to_rows, ButtonStyle, \
    component_callback, ComponentContext
import os
from dotenv import load_dotenv

import server.users
import server.deps
import server.tasks
from discord import modals
from discord.modals import select_user, update_user_modal, select_department, update_department_modal, \
    create_task_modal, update_task_modal, select_task

load_dotenv()

bot = Client(intents=Intents.ALL)
bot_token = os.getenv("BOT_TOKEN")
owner_guiId = None


@listen()
async def on_startup():
    global owner_guiId
    print("hey")
    owner_guiId = bot.owner.id
    status, response = server.users.get(owner_guiId)
    if status and response:
        print(f"Bot is ready!\nThis bot is coded by {bot.owner}")
    else:
        if server.users.create(name=bot.owner.username, guiId=bot.owner.id, phone="09393935921",
                               email="borsalani@chaleshsoft.com", is_manager=True):
            print(f"Bot is ready!\nThis bot is coded by {bot.owner}")
        else:
            raise "Bot is not connected to Database"


@slash_command(name="manage", description="managing data")
async def manage(ctx: SlashContext):
    userGuiId = ctx.user.id
    if userGuiId == owner_guiId:
        manage_buttons = spread_to_rows(
            Button(custom_id=f"manager_manage_users", style=ButtonStyle.PRIMARY, label="Users", ),
            Button(custom_id=f"manager_manage_departments", style=ButtonStyle.PRIMARY, label="Departments", ),
            Button(custom_id=f"manager_manage_tasks", style=ButtonStyle.PRIMARY, label="Tasks", ),
            max_in_row=3)
        await ctx.send(content="What Do You Want To Do?", components=manage_buttons, ephemeral=True, delete_after=600)
    else:
        status, users = server.users.get(userGuiId)
        if users:
            pass
        else:
            await ctx.send(content="Access Denied!\nNot a Registered User.", ephemeral=True, delete_after=5)


@component_callback("manager_manage_tasks")
async def manage_tasks(ctx: ComponentContext):
    buttons = spread_to_rows(
        Button(custom_id="tasks_create", style=ButtonStyle.GREEN, label="Create a Task", ),
        Button(custom_id="tasks_update", style=ButtonStyle.PRIMARY, label="Edit a Task", ),
        Button(custom_id="tasks_delete", style=ButtonStyle.RED, label="Delete a Task", ),
        max_in_row=3)
    await ctx.edit_origin(content="Select an Option", components=buttons)


@component_callback("tasks_create")
async def tasks_create(ctx: ComponentContext):
    await create_task_modal(ctx)


@component_callback("tasks_update")
async def tasks_update(ctx: ComponentContext):
    status, tasks = server.tasks.getAll()
    ongoing_tasks = []
    if status:
        for task in tasks:
            if task['manager_developer'] is None:
                ongoing_tasks.append(task)
    else:
        await ctx.edit_origin(content="Server is not responding properly", components=[])

    if ongoing_tasks:
        component = select_task(tasks, "Select a Task", "update_task_select")
        cancel_button = Button(custom_id=f"cancel", style=ButtonStyle.DANGER, label="Cancel")
        await ctx.edit_origin(components=spread_to_rows(component, cancel_button), content="pick a user to edit")
    else:
        await ctx.edit_origin(content="No tasks to edit", components=[])


@component_callback("update_task_select")
async def task_update_select(ctx: ComponentContext):
    values = ctx.values[0]
    task_id = values.split("___")[0]
    title = values.split("___")[1]
    deadline = values.split("___")[2]
    body = values.split("___")[3]
    dep = values.split("___")[4]
    task = {"id": task_id, "title": title, "deadline": deadline, "body": body, "dep_id": dep}
    await update_task_modal(task, ctx)
    await asyncio.sleep(2)
    await ctx.delete()


@component_callback("tasks_delete")
async def tasks_delete(ctx: ComponentContext):
    status, tasks = server.tasks.getAll()
    if status:
        if status:
            ongoing_tasks = []
            for task in tasks:
                if task['manager_developer'] is None:
                    ongoing_tasks.append(task)

        component = select_task(tasks, "Select a task", "delete_task_select")
        cancel_button = Button(custom_id=f"cancel", style=ButtonStyle.DANGER, label="Cancel")
        try:
            await ctx.edit_origin(components=spread_to_rows(component, cancel_button),
                                  content="Pick a task to Delete")
        except:
            await ctx.edit_origin(components=[], content="No tasks to select")
    else:
        await ctx.edit_origin(content="Server is not responding properly", components=[])


@component_callback('delete_task_select')
async def delete_task_select(ctx: ComponentContext):
    values = ctx.values[0]
    task_id = values.split("___")[0]
    title = values.split("___")[1]

    cancel_button = Button(custom_id=f"no_task_rm", style=ButtonStyle.DANGER, label="No")
    ok_button = Button(custom_id=f"yes_task_rm", style=ButtonStyle.GREEN, label="Yes")
    comp = spread_to_rows(ok_button, cancel_button)
    await ctx.edit_origin(
        content=f"You Are Deleting a Department with\n\nID: {task_id}\nTitle: {title}\n\n\n do you want to proceed?\n\n",
        components=comp)
    try:
        used_component = await bot.wait_for_component(components=comp, timeout=30)
        if used_component.ctx.custom_id == "no_task_rm":
            await cancel(used_component.ctx)
        elif used_component.ctx.custom_id == "yes_task_rm":
            status, response = server.tasks.delete(task_id)
            if status:
                await used_component.ctx.edit_origin(content=f"Task {title} Deleted Successfully!", components=[])
                await asyncio.sleep(2)
                await used_component.ctx.delete()
            else:
                await used_component.ctx.edit_origin(content="Server is not responding properly", components=[])
                await asyncio.sleep(2)
                await used_component.ctx.delete()
        else:
            pass
    except TimeoutError:
        await ctx.edit_origin(content="No Respond!", components=[])
        await asyncio.sleep(2)
        await ctx.delete()


@component_callback('manager_manage_departments')
async def manage_departments(ctx: ComponentContext):
    buttons = spread_to_rows(
        Button(custom_id="departments_create", style=ButtonStyle.GREEN, label="Create a Department", ),
        Button(custom_id="departments_update", style=ButtonStyle.PRIMARY, label="Edit a Department", ),
        Button(custom_id="departments_delete", style=ButtonStyle.RED, label="Delete a Department", ),
        max_in_row=3)
    await ctx.edit_origin(content="Select an Option", components=buttons)


@component_callback('departments_create')
async def department_create(ctx: ComponentContext):
    status, user_guiId = server.users.get(ctx.user.id)
    if status:
        await modals.create_department(ctx, user_guiId[0]['id'])
        await asyncio.sleep(2)
        await ctx.delete()
    else:
        await asyncio.sleep(2)
        await ctx.delete()


@component_callback('departments_update')
async def department_update(ctx: ComponentContext):
    status, departments = server.deps.getAll()
    if status:
        component = select_department(deps_list=departments, placeholder="Select a Department",
                                      custom_id="update_department_select")
        cancel_button = Button(custom_id="cancel", style=ButtonStyle.DANGER, label="Cancel")
        await ctx.edit_origin(components=spread_to_rows(component, cancel_button), content="pick a department to edit")
    else:
        await ctx.edit_origin(content="Server is not responding properly", components=[])
        await asyncio.sleep(2)
        await ctx.delete()


@component_callback("update_department_select")
async def department_update_select(ctx: ComponentContext):
    values = ctx.values[0]
    id = values.split("___")[0]
    title = values.split("___")[1]
    department = {"id": id, "title": title}
    await update_department_modal(department, ctx)
    await asyncio.sleep(2)
    await ctx.delete()


@component_callback("departments_delete")
async def department_delete(ctx: ComponentContext):
    status, deps = server.deps.getAll()
    if status:
        component = select_department(deps_list=deps, placeholder="Select a department",
                                      custom_id="delete_department_select")
        cancel_button = Button(custom_id=f"cancel", style=ButtonStyle.DANGER, label="Cancel")
        try:
            await ctx.edit_origin(components=spread_to_rows(component, cancel_button),
                                  content="Pick a Department to Delete")
        except:
            await ctx.edit_origin(components=[], content="No departments to select")
    else:
        await ctx.edit_origin(content="Server is not responding properly", components=[])


@component_callback('delete_department_select')
async def department_delete_select(ctx: ComponentContext):
    values = ctx.values[0]
    dep_id = values.split("___")[0]
    title = values.split("___")[1]

    cancel_button = Button(custom_id=f"no_dep_rm", style=ButtonStyle.DANGER, label="No")
    ok_button = Button(custom_id=f"yes_dep_rm", style=ButtonStyle.GREEN, label="Yes")
    comp = spread_to_rows(ok_button, cancel_button)
    await ctx.edit_origin(
        content=f"You Are Deleting a Department with\n\nID: {dep_id}\nTitle: {title}\n\n\n do you want to proceed?\n\n",
        components=comp)
    try:
        used_component = await bot.wait_for_component(components=comp, timeout=30)
        if used_component.ctx.custom_id == "no_dep_rm":
            await cancel(used_component.ctx)
        elif used_component.ctx.custom_id == "yes_dep_rm":
            status, response = server.deps.delete(dep_id)
            if status:
                await used_component.ctx.edit_origin(content=f"Department {title} Deleted Successfully!", components=[])
                await asyncio.sleep(2)
                await used_component.ctx.delete()
            else:
                await used_component.ctx.edit_origin(content="Server is not responding properly", components=[])
                await asyncio.sleep(2)
                await used_component.ctx.delete()
        else:
            pass
    except TimeoutError:
        await ctx.edit_origin(content="No Respond!", components=[])
        await asyncio.sleep(2)
        await ctx.delete()


@component_callback("manager_manage_users")
async def manage_users(ctx: ComponentContext):
    buttons = spread_to_rows(
        # Button(custom_id="users_create", style=ButtonStyle.GREEN, label="Create a User", ),
        Button(custom_id="users_update", style=ButtonStyle.PRIMARY, label="Edit a User", ),
        Button(custom_id="users_delete", style=ButtonStyle.RED, label="Delete a User", ),
        max_in_row=3)
    await ctx.edit_origin(content="Select an Option", components=buttons)


@component_callback('users_update')
async def users_update(ctx: ComponentContext):
    status, users = server.users.getAll()
    if status:
        component = select_user(users_list=users, placeholder="Select a User", custom_id="update_user_select")
        cancel_button = Button(custom_id=f"cancel", style=ButtonStyle.DANGER, label="Cancel")
        await ctx.edit_origin(components=spread_to_rows(component, cancel_button), content="pick a user to edit")
    else:
        await ctx.edit_origin(content="Server is not responding properly", components=[])


@component_callback('update_user_select')
async def user_update_select(ctx: ComponentContext):
    user_guiId = int(ctx.values[0])
    status, user = server.users.get(user_guiId)
    if status:
        await update_user_modal(user[0], ctx, user_guiId)
        await asyncio.sleep(2)
        await ctx.delete()
    else:
        await ctx.edit_origin(content="Server is not responding properly", components=[])
        await asyncio.sleep(2)
        await ctx.delete()


@component_callback("users_delete")
async def users_delete(ctx: ComponentContext):
    status, users = server.users.getAll()
    if status:
        component = select_user(users_list=users, placeholder="Select a User", custom_id="delete_user_select")
        cancel_button = Button(custom_id=f"cancel", style=ButtonStyle.DANGER, label="Cancel")
        try:
            await ctx.edit_origin(components=spread_to_rows(component, cancel_button), content="Pick a User to Delete")
        except:
            await ctx.edit_origin(components=[], content="No users to select")

    else:
        await ctx.edit_origin(content="Server is not responding properly", components=[])


@component_callback("delete_user_select")
async def delete_user_select(ctx: ComponentContext):
    user_guiId = int(ctx.values[0])
    status, user = server.users.get(user_guiId)
    if status:
        cancel_button = Button(custom_id=f"no", style=ButtonStyle.DANGER, label="No")
        ok_button = Button(custom_id=f"yes", style=ButtonStyle.GREEN, label="Yes")
        comp = spread_to_rows(ok_button, cancel_button)
        await ctx.edit_origin(
            content=f"You Are Deleting a User with\n\nID: {user[0]['id']}\nName: {user[0]['name']}\n\n\n do you want to proceed?\n\n",
            components=comp)
        try:
            used_component = await bot.wait_for_component(components=comp, timeout=30)
            if used_component.ctx.custom_id == "no":
                await cancel(used_component.ctx)
            elif used_component.ctx.custom_id == "yes":
                status, response = server.users.delete(user[0]['id'])
                if status:
                    await ctx.edit_origin(content=f"User {user[0]['id']} Deleted Successfully!", components=[])
                    await asyncio.sleep(2)
                    await ctx.delete()
                else:
                    await ctx.edit_origin(content="Server is not responding properly", components=[])
                    await asyncio.sleep(2)
                    await ctx.delete()
            else:
                pass
        except TimeoutError:
            await ctx.edit_origin(content="No Respond!", components=[])
            await asyncio.sleep(2)
            await ctx.delete()
    else:
        await ctx.edit_origin(content="Server is not responding properly", components=[])
        await asyncio.sleep(2)
        await ctx.delete()


@component_callback("cancel")
async def cancel(ctx: ComponentContext):
    await ctx.edit_origin(components=[], content="Canceled")
    await asyncio.sleep(2)
    await ctx.delete()



@slash_command(name="tasks", description="tasks")
async def jobs(ctx:SlashContext):
    userGuiId = ctx.user.id
    status, users = server.users.get(userGuiId)
    if status and users:
        task_buttons = spread_to_rows(
            Button(custom_id=f"my_tasks", style=ButtonStyle.PRIMARY, label="My Tasks", ),
            Button(custom_id=f"get_new_tasks", style=ButtonStyle.PRIMARY, label="Get New Tasks", ),
            max_in_row=3)
        await ctx.send(content="What Do You Want To Do?", components=task_buttons, ephemeral=True, delete_after=600)
    else:
        await ctx.send(content="Server is not responding properly", components=[])
        await asyncio.sleep(2)
        await ctx.delete()




bot.start(bot_token)
