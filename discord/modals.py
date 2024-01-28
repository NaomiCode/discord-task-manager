import datetime

from interactions import *
from server.users import update as update_server
import server.users
import server.deps
import server.tasks
import server


async def create_department(ctx: ComponentContext, guiId):
    create_department_modal = Modal(
        ShortText(
            label="Title",
            custom_id="title",
            placeholder="enter name of department",
            min_length=1,
            required=True
        ),
        title=f"Creating Department")
    await ctx.send_modal(create_department_modal)
    modal_ctx: ModalContext = await ctx.bot.wait_for_modal(create_department_modal)
    title = modal_ctx.responses["title"]
    status, response = server.deps.create(title=title, user_id=int(guiId))
    if status:
        await modal_ctx.send(f"Department with title {title} created", ephemeral=True, delete_after=5)
    else:
        await modal_ctx.send(content="Error! Something went wrong.", ephemeral=True, delete_after=5)


async def update_department_modal(Department: dict, ctx: ComponentContext):
    pre_title = Department['title']
    id = Department['id']
    update_department = Modal(
        ShortText(
            label="Title",
            custom_id="title",
            placeholder="Department Title",
            min_length=1,
            required=True,
            value=pre_title
        ),
        title=f"Update Department info of \nDepartment ID: {id}")
    await ctx.send_modal(update_department)
    modal_ctx: ModalContext = await ctx.bot.wait_for_modal(update_department)
    new_title = modal_ctx.responses["title"]
    status, response = server.deps.update(category_id=id, title=new_title)
    if status:
        await modal_ctx.send("Department updated Successfully!", ephemeral=True, delete_after=5)
    else:
        await modal_ctx.send(content="Error! Something went wrong.", ephemeral=True, delete_after=5)


async def update_user_modal(server_user: dict, ctx: ComponentContext, user_guiId: str | int):
    pre_name = server_user['name']
    pre_phone = server_user['phone']
    pre_guiId = server_user['guiId']
    pre_email = server_user['email']
    pre_is_manager = server_user['is_manager']
    id = server_user['id']
    update_user = Modal(
        ShortText(
            label="Name",
            custom_id="name",
            placeholder="user's name",
            min_length=1,
            required=False,
            value=pre_name
        ),
        ShortText(
            label="Phone Number",
            custom_id="phone",
            placeholder="Phone Number",
            min_length=11,
            max_length=11,
            required=False,
            value=pre_phone
        ),
        ShortText(
            label="GuiId",
            custom_id="guiId",
            placeholder="user's current GuiId",
            min_length=1,
            required=False,
            value=pre_guiId
        ),
        ShortText(
            label="Email",
            custom_id="email",
            placeholder="user's email address'",
            min_length=1,
            required=False,
            value=pre_email
        ),
        ShortText(
            label="Manager",
            custom_id="manager_status",
            placeholder="set True to make this user a manager",
            min_length=1,
            required=False,
            value=str(bool(pre_is_manager))
        ),
        title=f"Update User info of \nUser ID: {id}")
    await ctx.send_modal(update_user)
    modal_ctx: ModalContext = await ctx.bot.wait_for_modal(update_user)

    new_name = modal_ctx.responses["name"]
    new_phone = modal_ctx.responses["phone"]
    new_guiId = modal_ctx.responses["guiId"]
    new_email = modal_ctx.responses["email"]
    new_is_manager = modal_ctx.responses["manager_status"]
    status, response = update_server(userId=id, name=new_name, phone=new_phone, email=new_email,
                                     guiId=new_guiId, is_manager=new_is_manager)
    if status:
        await modal_ctx.send("User updated Successfully!", ephemeral=True, delete_after=5)
    else:
        await modal_ctx.send(content="Error! Something went wrong.", ephemeral=True, delete_after=5)

    return True


def select_user(users_list: list, custom_id: str, placeholder: str):
    if len(users_list) == 0:
        return None
    else:

        options: list[StringSelectOption] = []
        for i in range(len(users_list)):
            options.append(
                StringSelectOption(label=f"{users_list[i]['name']}", value=users_list[i]['guiId'],
                                   description=f"{users_list[i]['name']}"))
        component = StringSelectMenu(
            options,
            placeholder=placeholder,
            custom_id=custom_id
        )
        return component


def select_department(deps_list: list, placeholder: str, custom_id: str, def_val=None):
    if not (len(deps_list)):
        return None
    else:
        options: list[StringSelectOption] = []
        for i in range(len(deps_list)):
            options.append(
                StringSelectOption(label=f"{deps_list[i]['title']}",
                                   value=f"{deps_list[i]['id']}___{deps_list[i]['title']}",
                                   default=True if def_val == int(deps_list[i]['id']) else False))

        component = StringSelectMenu(
            options,
            placeholder=placeholder,
            custom_id=custom_id
        )
        return component


def select_task(tasks_list: list, placeholder: str, custom_id: str):
    if not (len(tasks_list)):
        return None
    else:
        options: list[StringSelectOption] = []
        for i in range(len(tasks_list)):
            options.append(
                StringSelectOption(label=f"{tasks_list[i]['title']}",
                                   value=f"{tasks_list[i]['id']}___{tasks_list[i]['title']}___{tasks_list[i]['deadline']}___{tasks_list[i]['body']}___{tasks_list[i]['category_id']}"))
        component = StringSelectMenu(
            options,
            placeholder=placeholder,
            custom_id=custom_id
        )
        return component


async def create_task_modal(ctx: ComponentContext):
    create_task_modal_component = Modal(
        ShortText(
            label="Title",
            custom_id="title",
            placeholder="enter task title",
            min_length=1,
            required=True
        ), ShortText(
            label="Description",
            custom_id="description",
            placeholder="enter task description",
            min_length=3,
            required=True
        ), ShortText(
            label="Deadline",
            custom_id="deadline",
            placeholder="enter task deadline in days",
            min_length=1,
            required=True
        ),
        title=f"Creating task")
    await ctx.send_modal(create_task_modal_component)
    modal_ctx: ModalContext = await ctx.bot.wait_for_modal(create_task_modal_component)
    title = modal_ctx.responses["title"]
    desc = modal_ctx.responses["description"]
    deadline = modal_ctx.responses["deadline"]
    creator_id = modal_ctx.user.id
    if deadline.isdigit():
        deadline = datetime.datetime.today().date() + datetime.timedelta(days=int(deadline))

        status, departments = server.deps.getAll()
        if status:
            component = select_department(deps_list=departments, placeholder="Select a Department",
                                          custom_id="create_task_department_select")
            await modal_ctx.send(content="select a department", components=component, ephemeral=True, delete_after=5)
            used_comp = await ctx.bot.wait_for_component(components=component)
            department = used_comp.ctx.values[0].split("___")[0]
            status, response = server.tasks.create(title=title, body=desc, deadline=deadline, created_id=creator_id,
                                                   category_id=department)
            if status:
                await used_comp.ctx.edit_origin(content="task created successfully", components=[])
            else:
                await used_comp.ctx.edit_origin(content="Error! server not responding", components=[])
    else:
        await modal_ctx.send(content="Error! only enter numbers in deadline section", ephemeral=True, delete_after=5)


async def update_task_modal(task: dict, ctx: ComponentContext):
    update_task_modal_component = Modal(
        ShortText(
            label="Title",
            custom_id="title",
            placeholder="enter task title",
            value=task['title'],
            min_length=1,
            required=True
        ), ShortText(
            label="Description",
            custom_id="description",
            placeholder="enter task description",
            value=task['body'],
            min_length=3,
            required=True
        ), ShortText(
            label="Deadline",
            custom_id="deadline",
            placeholder="enter task deadline in days",
            value=str(int((datetime.datetime.strptime(task['deadline'],
                                                      '%Y-%m-%d') - datetime.datetime.today()).total_seconds() / 86400)),
            min_length=1,
            required=True
        ),
        title="editing task")
    await ctx.send_modal(update_task_modal_component)
    modal_ctx: ModalContext = await ctx.bot.wait_for_modal(update_task_modal_component)
    title = modal_ctx.responses["title"]
    body = modal_ctx.responses["description"]
    deadline = modal_ctx.responses["deadline"]
    if deadline.isdigit():
        deadline = datetime.datetime.today().date() + datetime.timedelta(days=int(deadline))

        status, departments = server.deps.getAll()
        if status:
            component = select_department(deps_list=departments, placeholder="Select a Department",
                                          custom_id="update_task_department_select", def_val=int(task['dep_id']))
            await ctx.delete()
            await modal_ctx.send(content="select a department for the edited task", components=component,
                                 ephemeral=True, delete_after=10)
            used_comp = await ctx.bot.wait_for_component(components=component)
            department = used_comp.ctx.values[0].split("___")[0]
            status, response = server.tasks.update(task_id=task['id'], title=title, body=body, deadline=deadline,
                                                   category_id=department)
            if status:
                await used_comp.ctx.edit_origin(content="task updated successfully", components=[])
            else:
                await used_comp.ctx.edit_origin(content="Error! server not responding", components=[])
        else:
            await modal_ctx.send(content="Error! server not responding", components=[])
    else:
        await modal_ctx.send(content="Error! only enter numbers in deadline section", ephemeral=True, delete_after=5)
