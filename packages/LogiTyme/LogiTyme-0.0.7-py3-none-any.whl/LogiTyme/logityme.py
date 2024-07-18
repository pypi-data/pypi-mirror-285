"""
LogiTyme:
    LogiTyme is a Python package used to track the time spent on each function,
    custom functions, and the entire Python Program
"""

import cProfile
import json
import os
import pstats
from datetime import datetime
from pstats import SortKey, Stats
import tracemalloc
import sys
import uuid
from terminaltables import AsciiTable


class LogiTyme:
    def __init__(self, env, maxTime=5):
        self.__endTime = None
        self.__startTime = None
        self.__env = "local"
        self.__profiler = cProfile.Profile()
        self.__tracemalloc = tracemalloc
        self.__current_file_name = os.path.split(sys.argv[0])[1]
        self.__filenames = []
        self.__customProfile = None
        self.__filePath = "tmp/"
        self.__fileName = ""
        self.__maxTime = maxTime
        self.__maxtime = None
        self.__threshold_check_list = []
        self.__final_threshold_list = {}

    """
    createDir:
        This will create a directory with tmp only in local server.
    """

    def __createDir(self):
        if self.__env == "local":
            if not os.path.exists(self.__filePath):
                os.makedirs(self.__filePath)

    # Decorator to get the function name
    def smart_threshold_check(self, maxTimeLimit):
        def threshold_check(func):
            def check(*args):
                self.__threshold_check_list.append({str(func.__name__) + "_maxLimit": maxTimeLimit})
                return func(*args)

            return check

        return threshold_check

    """
    StartReport: 
        Is the feature used to start the process of logging the time for you python program.
    """

    def StartReport(self):
        self.__startTime = datetime.now()
        self.__profiler.enable()
        self.__tracemalloc.start()
        self.__createDir()

    #
    # def exclude_function(self, action):
    #     if action == "exclude":
    #         self.profiler.disable()
    #     else:
    #         self.profiler.enable()

    """
    __Env_Suggestions:
        Based on the time taken by the program, this feature suggest which cloud provider is best to use, if you want to run in cloud.
    """

    def __env_suggestions(self, time_taken):
        if time_taken <= 300:
            return f"\t- Short tasks (less than 5 minutes):\n\t\t-- GCP (Cloud Functions, Compute Engine, GKE, Cloud Run) or AWS (Lambda, EC2, ECS, Step Function, Glue): \n\t\t\t Both are well-suited for tasks that complete quickly.\n\t\t-- Azure Functions (Consumption Plan, VM, AKS, Container Instances):\n\t\t\t Good choice for short tasks"
        elif time_taken > 300 and time_taken < 900:
            return f"\t- Medium tasks (5 to 15 minutes):\n\t\t-- AWS EC2, ECS, EKS, Batch, Glue, Step Function: \n\t\t\t With a 15-minutes limit, AWS Lambda is ideal for tasks that require a bit more time.\n\t\t-- GCP Compute Engine, App Engine, GKE, Cloud Run:\n\t\t\t These services can handle longer execution time.\n\t\t-- Azure Functions (Premium or Dedicated Plan, VM, AKS, Container Instance):\n\t\t\t These plans can handle longer execution time."
        elif time_taken >= 900 and time_taken < 3600:
            return f"\t- Long tasks (15 to 60 minutes):\n\t\t-- AWS EC2, ECS, EKS, Glue, Step Function: \n\t\t\t Offers the flexibility to run tasks up to 60 minutes.\n\t\t-- GCP Compute Engine, GKE, App Engine (Standard Environment):\n\t\t\t These services are suitable for long tasks.\n\t\t-- Azure Functions (Premium or Dedicated Plan, AKS, Container Instance, VM): \n\t\t\t Offers the flexibility to run tasks up to 60 minutes.\n\t\t-- Docker Container:\n\t\t\t If any task duration exceeds the limit of any serverless functions, Docker Containers have no timeout, allowing for long-running, complex workloads."
        elif time_taken >= 3600:
            return f"\t- Very Long tasks (over 60 minutes):\n\t\t-- AWS EC2, ECS, EKS, Glue, Step Function:\n\t\t\t Suitable for very long tasks.\n\t\t-- GCP Compute Engine, GKE, App Engine (Flexible Environment):\n\t\t\t Suitable for very long tasks.\n\t\t-- Azure VM, AKS, Premium or Dedicated Plan:\n\t\t\t Suitable for very long tasks.\n\t\t-- Docker Container:\n\t\t\t If any task duration exceeds the limit of any serverless functions, Docker Containers have no timeout, allowing for long-running, complex workloads."

    """
    __reportTempalte:
        This will create a template of the report with the logged data for each function and entire code. and save it as a txt file (if needed)
    """

    def __reportTemplate(
            self, total_time, memory_consumed, functions, inbuilt_functions, saveFile
    ):
        report = f"\nPerformance Analysis\n\n"
        report += f"1. Introduction:\n"
        report += f"""\tThis report presents the findings of a performance analysis conducted on the Python program '{self.__current_file_name}'. The purpose of the analysis is to provide insights into the time consumed by the program and offer recommendations for optimizing its performance.\n\n"""
        report += f"2. Methodolgy:\n"
        report += f"""\tThe program was profiled using the cProfile module to collect data on execution time. The collected data was analyzed to identify the functions consuming the most time.\n\n"""

        report += f"3. Results:\n"
        report += f"""\t- Started the program at: {self.__startTime}\n\t- Ended the program at: {self.__endTime}\n\t- Total Execution Time: {total_time} seconds\n\t- As you defined the threshold limit as {self.__maxTime} mins, Since this script took {total_time < self.__maxTime * 60 and "Less then your threshold limit." or "More then your threshold limit."}\n\t- memory consumed: {round(memory_consumed, 4)}MB\n\n"""
        report += f"4. Functions Results:\n"

        functions_table = [["Function Name", "Time Consumed", "Maximum Threshold Limit Set"]]
        for items in functions.items():

            for i in items[1].items():
                if ("maxLimit" not in i[0]):
                    functions_table.append(
                        [i[0], str(round(i[1], 3)) + " secs", str(items[1][i[0] + "_maxLimit"] * 60) + " secs"])
        function_table = AsciiTable(functions_table)
        report += f"""{function_table.table}\n\n"""

        report += "5. inBuilt-functions Time-Consumed Report:\n"
        inbuilt_data = [["Function Name", "Time Consumed"]]
        for i in inbuilt_functions.items():
            inbuilt_data.append([i[0], str(round(i[1], 3)) + " secs"])
        inbuilt_table = AsciiTable(inbuilt_data)
        report += f"""{inbuilt_table.table}\n\n"""

        report += f"6. Environment Suggestions:\n"
        report += f"{self.__env_suggestions(total_time)}\n\n"
        report += f"7. Code Optimization:\n"
        functions_table = [["Function Name", "Time Consumed", "Maximum Threshold Limit Set"]]
        functions = functions.items()
        report_function_max_time = ""
        c = 0
        for function_items in functions:
            function = function_items[0]
            if round(function_items[1][function], 4) != 0:
                functions_table.append(
                    [function, str(round(function_items[1][function], 4)) + " secs",
                     str(function_items[1][function + "_maxLimit"] * 60) + " secs"]
                )
                c += 1
                report_function_max_time += f"""Since this function "{function}" took {round(function_items[1][function], 4)} secs is {round(function_items[1][function], 4) < function_items[1][function + "_maxLimit"] * 60 and "less then " + str(function_items[1][function + "_maxLimit"] * 60) + " seconds (i.e < " + str(function_items[1][function + "_maxLimit"]) + " mins). The function is quite optimized" or "is more then " + str(function_items[1][function + "_maxLimit"] * 60) + " seconds (i.e > " + str(function_items[1][function + "_maxLimit"]) + " mins). Try to optimze the function a bit more to decrease the time consumed by code running on serverless or docker container"} \n"""
        function_table = AsciiTable(functions_table)
        report += function_table.table + "\n"
        report += report_function_max_time + "\n"
        report += "8. Conclusion:\n"
        report += f"\tThe analysis revealed areas for potential optimization in the Python program '{self.__current_file_name}'. By implementing the recommendations outlined in this report, the program's performance can be improved, leading to better overall efficency"

        if saveFile:
            with open(
                    "Generated Report for " + self.__current_file_name + ".txt", "w"
            ) as f:
                f.writelines(report)
        else:
            print(report)

    """
    GenerateReport:
        This feature used to end the logging process and generate a report based on each function used in the code.
        Now this will start process the logged data and generate a report based on the time spent in each function used in your code.
        The generated report will provide insights into the performance if different functions
    """

    def GenerateReport(self, saveFile=False):
        self.__endTime = datetime.now()
        for i in self.__threshold_check_list:
            for items in i.items():
                self.__final_threshold_list[items[0]] = items[1]
        current, peak = self.__tracemalloc.get_traced_memory()
        self.__profiler.disable()
        stats = Stats(self.__profiler)
        res = str(stats)
        ttt = 0
        funcs = {}
        time_comsumed_inbuilt = {}
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            ttt += round(tt, 3)
            if self.__current_file_name in func[0]:
                funcss = {}
                funcss[func[2]] = round(ct, 3)
                funcss[func[2] + "_maxLimit"] = self.__final_threshold_list[func[2] + "_maxLimit"]

                funcs[func[2]] = funcss

            if "built-in" in func[2] and round(tt, 3) != 0.0:
                if func[2] not in time_comsumed_inbuilt:
                    time_comsumed_inbuilt[func[2]] = round(tt, 3)
                else:
                    time_comsumed_inbuilt[func[2]] += round(tt, 33)

        for files in self.__filenames:
            filename = files[0]['name']
            stat1 = pstats.Stats(
                self.__filePath + filename + ".prof"
                if self.__env == "local"
                else self.__filePath + filename + ".prof"
            ).sort_stats("tottime")
            stats_total_tile = 0
            for func, (cc, nc, tt, ct, callers) in stat1.stats.items():
                stats_total_tile += round(tt, 3)
                # time_comsumed_by_other_files += round(tt,3)
                if "built-in" in func[2] and round(tt, 3) != 0.0:
                    if func[2] not in time_comsumed_inbuilt:
                        time_comsumed_inbuilt[func[2]] = round(tt, 3)
                    else:
                        time_comsumed_inbuilt[func[2]] += round(tt, 33)
            funcss = {}

            funcss[filename] = stats_total_tile
            funcss[filename + '_maxLimit'] = files[0]['maxLimit']
            funcs[filename] = funcss

        # exit()
        for files in self.__filenames:
            filename = files[0]['name']
            os.remove(
                self.__filePath + filename + ".prof"
                if self.__env == "local"
                else self.__filePath + filename + ".prof"
            )
        self.__filenames = []
        time_comsumed_inbuilt = dict(
            sorted(
                time_comsumed_inbuilt.items(), reverse=True, key=lambda item: item[1]
            )
        )
        self.__reportTemplate(
            total_time=round(ttt, 3),
            memory_consumed=current / 10 ** 6,
            functions=funcs,
            inbuilt_functions=time_comsumed_inbuilt,
            saveFile=saveFile,
        )

    """
    LogiFunctStart & LogiFuncEnd:
        This feature is used to log time for custom code.
    """

    def LogiFuncStart(self, name="default", maxLimit=5):
        if name == "default":
            name = str(uuid.uuid4())
            self.__fileName = name
            self.__maxLimit = maxLimit
        else:
            if os.path.exists(
                    self.__filePath + name + ".prof"
                    if self.__env == "local"
                    else self.__filePath + name + ".prof"
            ):
                name = name + "_" + str(uuid.uuid4())
                self.__fileName = name
            else:
                self.__fileName = name
        self.__customProfile = cProfile.Profile()
        self.__customProfile.enable()
        self.__filenames.append([{"name": name, "maxLimit": maxLimit}])

    def LogiFuncEnd(self):
        name = self.__fileName
        Stats(self.__customProfile).strip_dirs().sort_stats("ncalls").dump_stats(
            self.__filePath + name + ".prof"
            if self.__env == "local"
            else self.__filePath + name + ".prof"
        )
        self.__customProfile.disable()
        self.__customProfile = None
        self.__fileName = ""
        self.__profiler.enable()
