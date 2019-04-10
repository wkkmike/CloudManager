import Manager

commands = {0:"help",
            1:"create_service_from_yml",
            2:"list_all_service",
            3:"run_service",
            4:"check_stats_of_service"}

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
    elif(user_input == "1"):
        image_name = input("What is the image name?\nEnter: ")
        file_name = input("What is the file name?\nEnter: ")
        upper = input("What is the upper limit for this image?:(default is 10)"
                      "\n Enter")
        lower = input("What is the lower limit for this image?:(default is 1)"
                      "\n Enter")
        try:
            u = int(upper)
            l = int(lower)
        except:
            u = 10
            l = 1
            print("Invalid input, use default setting")
        if u < l or l < 0:
            u = 10
            l = 1
            print("Invalid input, use default setting")
        print(manager.create_service_from_yml(image_name, file_name, u, l))
    elif(user_input =="2"):
        print(manager.list_all_service())
    elif (user_input == "3"):
        image_name = input("What is the image name?\nEnter: ")
        amount = input("How many worker do you need?\nEnter: ")
        print(manager.run_service(image_name,amount))
    elif(user_input == "4"):
        name = input("What is the service name?\nEnter: ")
        print(manager.check_health_of_service(name))
    else:
        print("type help to see all commands")
