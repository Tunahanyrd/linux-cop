import sys, os
sys.dont_write_bytecode=True

os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GRPC_LOG_SEVERITY"] = "ERROR"

os.environ["GLOG_minloglevel"] = "3"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

sys.stderr = open(os.devnull, "w")
