import threading
import os
import shutil
import csv
from datetime import datetime

# Class to handle the necessary logging functionalities
class CSVLogger:
    def __init__(self, filename):
        self.filename = filename
        self.fieldnames = ['timestamp', 'operation','source_folder','replica_folder', 'changed_dirs']
        
        # Write header if file is new
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                writer.writeheader()
    
    def log(self, operation, source_folder, replica_folder, dirs):
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'operation':operation,
            'source_folder': os.path.relpath(source_folder),
            'replica_folder': os.path.relpath(replica_folder),
            'changed_dirs': dirs,
        }
        print("LOG:",*list(log_entry.values()))
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            writer.writerow(log_entry)
    
    def create_log(self, source_folder, replica_folder, dirs):
        self.log('CREATE', source_folder, replica_folder, dirs)
    
    def copy_log(self, source_folder, replica_folder, dirs):
        self.log('COPY', source_folder, replica_folder, dirs)
    
    def delete_log(self, source_folder, replica_folder, dirs):
        self.log('DELETE', source_folder, replica_folder, dirs)    

# Class to handle the synchronization processes
class SyncThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.sleep_flag = threading.Event()
        self.sync_interval = 1
        self.log_file = None

        self.source_path = None
        self.replica_path = None
    
    def run(self) -> None:
        while True:
            self.sleep_flag.wait(self.sync_interval)

            if self.source_path and self.replica_path:
                self.source_files = set(os.path.relpath(os.path.join(dirpath, file) ,self.source_path)
                    for dirpath, dirnames, filenames in os.walk(self.source_path) 
                    for file in filenames + dirnames)

                self.replica_files = set(os.path.relpath(os.path.join(dirpath, file) ,self.replica_path)
                    for dirpath, dirnames, filenames in os.walk(self.replica_path) 
                    for file in filenames + dirnames)

                replica_extra_files = self.replica_files - self.source_files
                source_extra_files = self.source_files - self.replica_files

                shutil.copytree(self.source_path,self.replica_path,dirs_exist_ok=True)

                if not self.log_file == None and not len(source_extra_files) == 0:
                    self.log_file.create_log(self.source_path,
                                             self.replica_path,
                                             str(source_extra_files)
                                             )

                for extra_file in replica_extra_files:
                    if os.path.exists(os.path.join(self.replica_path,extra_file)):
                        shutil.rmtree(os.path.join(self.replica_path,extra_file), ignore_errors=True)
                        try:
                            os.remove(os.path.join(self.replica_path,extra_file))
                        except:
                            pass
                        if not self.log_file == None and not os.path.exists(os.path.join(self.replica_path,extra_file)):
                            self.log_file.delete_log(self.source_path,
                                                    self.replica_path,
                                                    str(replica_extra_files))

running = True
option = None    

thread = SyncThread()
thread.daemon = True
thread.start()

# Main thread menu
while running:
    print("1 - Set source folder")
    print("2 - Set replica folder:")
    print("3 - Set log file path")
    print("4 - Set synchronization interval")
    print("5 - Show info")
    print("6 - Exit program")
    print()                                                    

    option = input("Select your option: ")
    
    match option:
        case "1": # Source folder update case
            source_aux = input("The source relative folder path is: ")
            if not os.path.isabs(source_aux):
                source_path = os.getcwd() + "\\" + source_aux
            else:
                print("Not a relative path received. Source path not updated")
                continue      
            if not os.path.exists(source_path):
                print("This folder does not exist")
                option = input("Do you want to create this directory?(y/n)")
                if option == "y" or option == "Y":
                    os.mkdir(source_path)
                    thread.source_path = source_path
                    print("New source folder created and updated")
                elif option == "n" or option == "N":
                    print("Source folder update canceled")            
                    print("Current source folder path:", thread.source_path)            
                else:
                    print("INVALID OPTION")
            else:
                thread.source_path = source_path
        case "2": # Replica folder update case
                replica_aux = input("The replica relative folder path is: ")
                if not os.path.isabs(replica_aux):
                    replica_path = os.getcwd() + "\\" + replica_aux
                else:
                    print("Not a relative path received. Replica path not updated")         
                    continue      
                # replica_path = os.path.abspath(replica_aux)
                if not os.path.exists(replica_path):
                    print("This folder path does not exist")
                    option = input("Do you want to create this directory?(y/n)")
                    if option == "y" or option == "Y":
                        os.mkdir(replica_path)
                        thread.replica_path = replica_path
                        print("New replica folder created and updated")
                    elif option == "n" or option == "N":
                        print("Replica folder update canceled")            
                        print("Current replica folder path:", thread.replica_path)            
                    else:
                        print("INVALID OPTION") 
                else:
                    print("If you use this folder as replica, original content will be permanently lost.")
                    option = input("Do you want to use this directory as replica folder?(y/n)")
                    if option == "y" or option == "Y":
                        print("Replica folder updated")
                        thread.replica_path = replica_path
                    elif option == "n" or option == "N":
                        print("Replica folder update canceled")            
                        print("Current replica folder path:", thread.replica_path)            
                    else:
                        print("INVALID OPTION")                     

        case "3": # Set log file
            thread.log_file = CSVLogger(input("The log file path is: "))
        case "4": # Synchronization interval
            thread.sync_interval = int(input("Update synchronization interval for: "))
        case "5": # Show info
            print()
            print()
            print("Source folder path:",thread.source_path)
            print("Replica folder path:",thread.replica_path)
            print("Log file path:",thread.log_file.filename)
            print("Synchronization interval:",thread.sync_interval)
            print()    
            print()    
        case "6": # Exit
            print("Thank you for taking this challenge!!!! See you next time!!! ")
            running = False
        case _:
            print("INVALID OPTION")        
            continue        

    # Check variables for debugging
                                               




