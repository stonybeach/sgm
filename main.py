from glossarymaker import glossarymaker
import sys, configparser

default_dict = './JMdict_kata'
default_sakura = "http://localhost:8080"

def process(novel, start, end, jmdict, sakura_server, current_mapping_file, output_mapping_file, least, min_len):
    g=glossarymaker()
    g.count_novel_kata(novel,start,end)
    g.del_simple(min_len)
    g.del_least(least)
    g.load_dict(jmdict)
    g.del_kata_in_dict()
    if current_mapping_file is not None:
        g.del_current(current_mapping_file)
    g.use_sakura(sakura_server)
    s = g.get_glossary()
    with open(output_mapping_file,'w') as out:
        out.write(s)
    print(s)
    print("Results are written to: " + output_mapping_file)

def use_config(config_file):
    print("Using configuration: " + config_file)
    config = configparser.ConfigParser()
    config.read(config_file)
    novel = config["syotesu"]["novel"]
    start = config["syotesu"].getint("start")
    end = config["syotesu"].getint("end")
    jmdict = config["translation"].get("dict", default_dict)
    sakura_server = config["translation"].get("sakura_server", default_sakura)
    if "current_mapping_file" in config["translation"]:
        current_mapping_file = config["translation"]["current_mapping_file"]
    output_mapping_file = config["translation"]["output_mapping_file"]
    least = config["translation"].getint("least_count",2)
    min_len = config["translation"].getint("min_len",3)
    print("novel = " + novel + " [" + str(start) + ", " + str(end) + "]")
    print("dict = " + jmdict)
    print("sakura_server = " + sakura_server)
    print("current_mapping_file = " + current_mapping_file)
    print("output_mapping_file = " + output_mapping_file)
    print("least_count = " + str(least))
    print("min_len = " + str(min_len))
    process(novel, start, end, jmdict, sakura_server, current_mapping_file, output_mapping_file, least, min_len)

def main():
    if len(sys.argv) > 1:
        use_config(sys.argv[1])
    else:
        print ("usage: python3 main.py <config_file>")

if __name__ == "__main__":
    main()
