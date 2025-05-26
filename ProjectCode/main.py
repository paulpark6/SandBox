# main.py
from methods import load_recent_keys, save_recent_keys
from llm_methods import store_response,convert_response
def main():
    # load or initialize stack
    recent_keys_dic   = load_recent_keys()
    recent_keys_stack = list(recent_keys_dic) # stack of dictinoaries

    ## ...

    # finally, persist any changes
    save_recent_keys(recent_keys_dic)

if __name__ == "__main__":
    main()
