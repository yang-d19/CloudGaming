import json
import os, sys

from sqlalchemy import false, true
from helper import *
from statistics import mean, stdev, median
from json_process import *
import numpy as np

args = sys.argv[1:]
argc = len(args)

#################################################
######## START: CHROMIUM LOGS PROCESSING ########
#################################################

platform_list = ["stadia", "luna", "gfn"]

TAGS = {
    "count": "count",
    "time_ms": "time_ms",
    "ssrc": "ssrc",
    "total_bps": "totbps",
    "net_fps": "nfps",
    "dec_fps": "dfps",
    "ren_fps": "rfps",
    "current_delay": "cur",
    "jb_delay": "jbd",
    "jb_cuml_delay": "jbcd",
    "jb_emit_count": "jbec",
    "decode_delay": "dec",
    "width": "w",
    "height": "h",
    "frame_drop": "fd",
    "freeze_count": "fc",
    "pause_count": "pc",
    "total_freezes_duration_ms": "tfd",
    "total_pauses_duration_ms": "pd",
    "total_frames_duration_ms": "tfmd",
    "sync_offset_ms": "sync",
    "sum_squared_frame_durations": "ssfd",
    "total_squared_inter_frame_delay": "tsif",
    "first_frame_received_to_decoded_ms": "ffrd",
    "frames_decoded": "fdec",
    "frames_rendered": "fren",
    "max_decode_ms": "mdec",
    "rx_bps": "rxbps",
    "rtx_bps": "rtxbps",
    "target_delay_ms": "tar",
    "min_playout_delay_ms": "minpd",
    "render_delay_ms": "ren",
    "total_decode_time_ms": "tdec",
    "total_inter_frame_delay": "tifd",
    "interframe_delay_max_ms": "ifdm"
}

STREAMFILE = "videoReceiveStream.txt"
RTCSTATS = "rtcStatsCollector.txt"
LOGFILE = "bot_log.csv"


def process_videoReceiveStream_log(path):

    print("Processing chromium VRS stats in: {}".format(path))

    # Path directory fix
    if path[-1] != "/":
        path += "/"

    # CHECK FOR LOG FILE
    log_data = ""
    log_start = 0
    log_end = 0

    if os.path.isfile(path + LOGFILE):
        log_data = open(path + LOGFILE, "r").read().split("\n")
    elif os.path.isfile(path + "log.csv"):
        log_data = open(path + "log.csv", "r").read().split("\n")

    if len(log_data) > 0:
        for e in log_data:
            if len(e) > 1:
                e = e.split(",")

                if log_start == 0:
                    log_start = float(e[0]) / 1000000000.00
                else:
                    log_end = float(e[0]) / 1000000000.00

    data = open(path + STREAMFILE, 'r').read().split("\n")
    data_dict = {}

    ts_start = 0

    tags_list = list(TAGS.keys())

    N = len(data)
    progress = 0
    progress_threshold = int(N * 0.25) + 1

    for line in data:
        if line.find("VRSSTATS") > 0:

            line = line.split(",")
            ts_mili = float(line[1]) / 1000.00
            if ts_start == 0:
                ts_start = ts_mili
            process = False

            if log_start > 0 and log_start <= ts_mili and log_end >= ts_mili:
                process = True

            if process == True:
                # print(ts_mili)
                ssrc = ""
                for i in range(3, len(line)):
                    # print(item)
                    stat = line[i].split(":")
                    # print(stat[0], TAGS["ssrc"])
                    if stat[0] == TAGS["ssrc"]:
                        ssrc = stat[1]
                        if ssrc not in list(data_dict.keys()):
                            data_dict[ssrc] = {}

                            for tag in tags_list:
                                # tag = TAGS[tag]
                                if tag == "count":
                                    data_dict[ssrc][TAGS["count"]] = 0
                                else:
                                    if tag not in ["ssrc"]:
                                        data_dict[ssrc][tag] = []

                        data_dict[ssrc][TAGS["count"]] += 1
                        data_dict[ssrc][TAGS["time_ms"]].append(ts_mili)

                    for tag in tags_list:
                        tag_val = TAGS[tag]
                        if stat[0] == tag_val and tag_val not in [
                                TAGS["time_ms"], "ssrc"
                        ]:
                            data_dict[ssrc][tag].append(float(stat[1]))
                            break

        # Progress tracking
        progress += 1
        if progress % progress_threshold == 0:
            print("Parsed {}%".format(int(progress * 100.0 / N)))

    writeDict(path + "parsed_videoReceiveStream.json", data_dict)

    print("Parsed {}%".format(int(progress * 100.0 / N)))

    # Generate video summary statistitcs
    # ssrc_list = list(data_dict.keys())
    # ssrc = ""
    # maxi = 0
    # summary_dict = {}

    # for ent in ssrc_list:
    #     if data_dict[ent][TAGS["count"]] > maxi:
    #         ssrc = ent
    #         maxi = data_dict[ent][TAGS["count"]]

    # for tag in tags_list:
    #     if tag not in ["count", "ssrc"]:
    #         summary_dict[tag] = {
    #             "mean": mean(data_dict[ssrc][tag]),
    #             "stdev": stdev(data_dict[ssrc][tag]),
    #             "median": median(data_dict[ssrc][tag]),
    #             "min": min(data_dict[ssrc][tag]),
    #             "max": max(data_dict[ssrc][tag])
    #         }

    # writeDict(path + "vrs_summary_stats.json", summary_dict)


def process_rtcStatsCollector_log(path):

    print("Processing chromium RTC stats in: {}".format(path))

    # Path directory fix
    if path[-1] != "/":
        path += "/"

    # CHECK FOR LOG FILE
    # log_file_path = path+LOGFILE
    log_data = ""
    log_start = 0
    log_end = 0

    if os.path.isfile(path + LOGFILE):
        log_data = open(path + LOGFILE, "r").read().split("\n")
    elif os.path.isfile(path + "log.csv"):
        log_data = open(path + "log.csv", "r").read().split("\n")

    if len(log_data) > 0:
        for e in log_data:
            if len(e) > 1:
                e = e.split(",")

                if log_start == 0:
                    log_start = float(e[0]) / 1000000000.00
                else:
                    log_end = float(e[0]) / 1000000000.00

    # print("PATH: ", path)
    # print("LOG TS:", log_start, log_end, log_end - log_start, "\n")

    data = open(path + RTCSTATS, 'r').read().split("\n")
    # print("LINES:", len(data))
    data_dict = {}

    ts_start = 0

    tags_list = list(TAGS.keys())

    # latest packet loss
    previous_loss = -1
    correct_loss = 0

    loss_d = {}
    for kk in ['audio', 'video']:
        loss_d[kk] = {}
        loss_d[kk]['previous_loss'] = -1
        loss_d[kk]['correct_loss'] = -1

    N = len(data)
    progress = 0
    progress_threshold = int(N * 0.25) + 1

    for line in data:
        tmp_line = line.split(",")
        ts_mili = float(tmp_line[1]) / 1000.00
        if ts_start == 0:
            ts_start = ts_mili

        process = False

        if log_start > 0 and log_start <= ts_mili and log_end >= ts_mili:
            process = True

        first_bracket = -10
        last_bracket = -10
        if process == True:
            for i, ent in enumerate(line):
                if ent == "{" and first_bracket == -10:
                    first_bracket = i
                if ent == "}":
                    last_bracket = i
                    dict_line = json.loads(line[first_bracket:last_bracket +
                                                1])
                    first_bracket = -10

                    media_type = ""

                    l_type = ""
                    l_id = ""
                    for lk in list(dict_line.keys()):
                        if lk == "type":
                            l_type = dict_line[lk]
                        if lk == "type" and dict_line[lk] not in list(
                                data_dict.keys()):
                            data_dict[l_type] = {}

                        if lk == "id":
                            l_id = dict_line[lk]
                        if lk == "id" and dict_line[lk] not in list(
                                data_dict[l_type].keys()):
                            data_dict[l_type][l_id] = {}

                        if lk == "mediaType":
                            media_type = dict_line[lk]

                        #### Latest version for packet loss adjustment based on duplicates and out of order
                        # Packetslost check is added because of negative values
                        # https://groups.google.com/g/discuss-webrtc/c/YXs7nG6FD48?pli=1
                        # RFC 3550

                        if lk not in ["type", "id"]:
                            if lk == "packetsLost" and media_type in [
                                    'audio', 'video'
                            ]:
                                if lk not in list(
                                        data_dict[l_type][l_id].keys()):
                                    if dict_line[lk] < 0:
                                        loss_d[media_type]['correct_loss'] = 0
                                        loss_d[media_type]['previous_loss'] = 0
                                        data_dict[l_type][l_id][lk] = [
                                            loss_d[media_type]['correct_loss']
                                        ]
                                    else:
                                        loss_d[media_type][
                                            'correct_loss'] = dict_line[lk]
                                        loss_d[media_type][
                                            'previous_loss'] = dict_line[lk]
                                        data_dict[l_type][l_id][lk] = [
                                            loss_d[media_type]['correct_loss']
                                        ]
                                else:
                                    if dict_line[lk] < 0:
                                        data_dict[l_type][l_id][lk].append(
                                            loss_d[media_type]['correct_loss'])
                                        loss_d[media_type][
                                            'previous_loss'] = dict_line[lk]

                                    else:
                                        if loss_d[media_type][
                                                'previous_loss'] < 0 and loss_d[
                                                    media_type][
                                                        'previous_loss'] < dict_line[
                                                            lk]:
                                            loss_d[media_type][
                                                'correct_loss'] += dict_line[
                                                    lk] - loss_d[media_type][
                                                        'previous_loss']

                                        elif loss_d[media_type][
                                                'previous_loss'] >= 0 and loss_d[
                                                    media_type][
                                                        'previous_loss'] < dict_line[
                                                            lk]:
                                            loss_d[media_type][
                                                'correct_loss'] += dict_line[
                                                    lk] - loss_d[media_type][
                                                        'previous_loss']

                                        loss_d[media_type][
                                            'previous_loss'] = dict_line[lk]
                                        data_dict[l_type][l_id][lk].append(
                                            loss_d[media_type]['correct_loss'])
                            else:
                                if lk not in list(
                                        data_dict[l_type][l_id].keys()):
                                    data_dict[l_type][l_id][lk] = [
                                        dict_line[lk]
                                    ]
                                else:
                                    data_dict[l_type][l_id][lk].append(
                                        dict_line[lk])

        # Progress tracking
        progress += 1
        if progress % progress_threshold == 0:
            print("Parsed {}%".format(int(progress * 100.0 / N)))

    # writeDict(path + "parsed_rtcStatsCollector.json", data_dict)

    # print("Parsed {}%".format(int(progress * 100.0 / N)))

    # Generate RTT summary
    rtt_key = "currentRoundTripTime"
    types_list = list(data_dict.keys())
    summary_dict = {}
    rtt_l = []
    ts_l = []
    found = 0

    for type_ in types_list:
        for id_ in list(data_dict[type_].keys()):
            if rtt_key in list(data_dict[type_][id_].keys()):
                rtt_l = data_dict[type_][id_][rtt_key]
                ts_l = data_dict[type_][id_]["timestamp"]
                found = 1
                break
        if found == 1:
            break

    for i, val in enumerate(rtt_l):
        rtt_l[i] = val * 1000
        ts_l[i] = ts_l[i] / 1000000.0

    summary_dict = {
        "rtts": rtt_l,
        "ts": ts_l,
        "mean": mean(rtt_l),
        "stdev": stdev(rtt_l),
        "median": median(rtt_l),
        "min": min(rtt_l),
        "max": max(rtt_l)
    }

    writeDict(path + "current_rtt.json", summary_dict)

    # Generate summary packet loss stats
    # type_ = "inbound-rtp"
    # search_key = "RTCInboundRTPVideoStream"

    # summary_dict = {}
    # packetsLost_l = []
    # packetsReceived_l = []
    # ts_l = []
    # found = 0

    # for id_ in list(data_dict[type_].keys()):
    #     if id_.find(search_key) >= 0:
    #         if "packetsReceived" in list(data_dict[type_][id_].keys()):
    #             packetsReceived_l = data_dict[type_][id_]["packetsReceived"]
    #             packetsLost_l = data_dict[type_][id_]["packetsLost"]
    #             ts_l = data_dict[type_][id_]["timestamp"]
    #             found = 1
    #             break

    # for i, val in enumerate(ts_l):
    #     ts_l[i] = ts_l[i] / 1000000.0

    # summary_dict = {
    #     "packetsReceived": packetsReceived_l,
    #     "ts": ts_l,
    #     "packetsLost": packetsLost_l
    # }

    # writeDict(path + "packet_loss_stats.json", summary_dict)


#################################################
######## END: CHROMIUM LOGS PROCESSING ##########
#################################################


def get_data_directories(path):
    raw_data_path_list = open(path, "r").read().split("\n")[1:]

    data_path_list = []

    for entry in raw_data_path_list:
        if len(entry) > 2:
            entry = entry.split(",")
            data_path_list.append((entry[0], entry[1], entry[2]))

    return data_path_list


def proc_every_day():
    # flag = 0
    # convert all data to csv
    for path in data_path_list:
        print(path)
        # print(path.split('\\')[-1])
        folder_name = path.split('\\')[-1]
        platform = folder_name.split('_')[1]
        if platform == 'stadia':
            # process_videoReceiveStream_log(path)
            # process_rtcStatsCollector_log(path)
            convert_to_csv(path)

def get_day_detailed():
    with open('day_detailed.csv', mode='w', newline='') as fp:
        wt = csv.writer(fp, delimiter=',')
        wt.writerow(['platform', 'game', 'date', 'ts', 'rtt', 'bitrate', 'fps',
            'jb_delay', 'max_decode_ms'])
        for path in data_path_list:
            # print(path)
            # folder = path.split('\\')[-1]
            folder_name = path.split('\\')[-1]
            folder_name = folder_name.split('_')

            game = folder_name[0]
            platform = folder_name[1]
            month_day = folder_name[-1]
            # month = month_day[0:2]
            # day = month_day[2:4]

            sum_file_path = f"{path}\summary.csv"
            if platform == 'stadia':
                print(path)
                with open(sum_file_path) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    line_count = 0
                    for record in csv_reader:
                        line_count += 1
                        if line_count == 1:
                            continue
                        wt.writerow([platform, game, month_day, record[0], record[1], record[2], 
                            record[3], record[4], record[5]])

                # platform, game, month_day, mean_rtt, mean_bitrate, mean_fps \
                #     = day_sum(path)
                # wt.writerow([platform, game, month_day, mean_rtt, mean_bitrate, mean_fps])


def get_day_summary():
    with open('new_day_sum.csv', mode='w', newline="") as fp:
        wt = csv.writer(fp, delimiter=',')
        wt.writerow(['platform', 'game', 'date', 'rtt', 'bitrate', 'fps',
            'jb_delay', 'max_decode_ms'])

        # extract every day's summary
        for path in data_path_list:
            print(path)
            folder = path.split('\\')[-1]
            if folder.split('_')[1] == 'stadia':
                platform, game, month_day, mean_rtt, mean_bitrate, mean_fps, \
                    mean_jbdelay, mean_maxdecodems = day_sum(path)
                wt.writerow([platform, game, month_day, mean_rtt, mean_bitrate, mean_fps, 
                    mean_jbdelay, mean_maxdecodems])


def calc_coef():
    with open('bps_rtt_coef.csv', mode='w', newline="") as fp:
        wt = csv.writer(fp, delimiter=',')
        wt.writerow(['platform', 'game', 'date', 'coef'])

        # extract every day's summary
        for path in data_path_list:
            print(path)
            folder_name = path.split('\\')[-1]
            folder_name = folder_name.split('_')

            game = folder_name[0]
            platform = folder_name[1]
            month_day = folder_name[-1]
            month = month_day[0:2]
            day = month_day[2:4]

            sum_file_path = f"{path}\{month}-{day}-summary.csv"

            if platform == 'stadia':
                with open(sum_file_path) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    rtt_list = []
                    bitrate_list = []
                    line_count = 0
                    for record in csv_reader:
                        line_count += 1
                        if line_count == 1:
                            continue
                        rtt_list.append(float(record[1]))
                        bitrate_list.append(float(record[2]))
                    pccs = np.corrcoef(rtt_list, bitrate_list)
                    p_coef = pccs[0][1]
                    wt.writerow([platform, game, month_day, p_coef])
        
def calc_bps_decode_coef():
    with open('new_day_sum.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        acv_decode_list = []
        acv_bitrate_list = []
        crew2_decode_list = []
        crew2_bitrate_list = []
        fc5_decode_list = []
        fc5_bitrate_list = []

        decode_list = []
        bitrate_list = []

        line_count = 0
        for record in csv_reader:
            line_count += 1
            if line_count == 1:
                continue
            
            decode_list.append(float(record[7]))
            bitrate_list.append(float(record[4]))

            if record[1] == 'acv':
                acv_decode_list.append(float(record[7]))
                acv_bitrate_list.append(float(record[4]))
            elif record[1] == 'crew2':
                crew2_decode_list.append(float(record[7]))
                crew2_bitrate_list.append(float(record[4]))
            else:
                fc5_decode_list.append(float(record[7]))
                fc5_bitrate_list.append(float(record[4]))


        acv_pccs = np.corrcoef(acv_decode_list, acv_bitrate_list)
        crew2_pccs = np.corrcoef(crew2_decode_list, crew2_bitrate_list)
        fc5_pccs = np.corrcoef(fc5_decode_list, fc5_bitrate_list)
        acv_p = acv_pccs[0][1]
        crew2_p = crew2_pccs[0][1]
        fc5_p = fc5_pccs[0][1]

        pccs = np.corrcoef(decode_list, bitrate_list)
        p = pccs[0][1]
        print(p, acv_p, crew2_p, fc5_p)


if __name__ == "__main__":

    data_path_list = []
    dataset_path = '.\dataset'
    platform_folders = os.listdir(dataset_path)

    print(platform_folders)
     
    for platform_folder in platform_folders:
        platform_path = os.path.join(dataset_path, platform_folder)
        leaf_folders = os.listdir(platform_path)

        for leaf_folder in leaf_folders:
            leaf_path = os.path.join(platform_path, leaf_folder)
            data_path_list.append(leaf_path)
            # print(leaf_path)

    # print(data_path_list)
    # proc_every_day()

    # proc_every_day()
    # get_day_detailed()

    calc_bps_decode_coef()