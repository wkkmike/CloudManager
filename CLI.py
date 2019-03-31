import Manager
commands = {0:"help",
            1:"create_service_from_yml"}

def print_commands():
    print("All Commands:")
    for c in commands:
        print(str(c) + ": " + commands.get(c))

manager = Manager.Manager("http://127.0.0.1:2379","docker-compose.yml")


print_commands()
while True:
    user_input = input("Enter: ")

    if(user_input=="help"):
        print_commands()
    elif(user_input =="exit"):
        break
    elif(user_input == "create_service_from_yml"):
        image_name = input("What is the image name?\nEnter: ")
        file_name = input("What is the file name?\nEnter: ")
        manager.create_new_service(image_name, file_name)

    else:
        print("type help to see all commands")
