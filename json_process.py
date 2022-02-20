import json
import math
import csv
import pytz
import datetime

def convert_to_csv(path):

    path = path + '\\'

    with open(path + 'current_rtt.json') as f:
        rtt_data = json.load(f)
    
    video_data = {}

    with open(path + 'parsed_videoReceiveStream.json') as f:
        top_video_data = json.load(f)
        for number in top_video_data:
            video_data = top_video_data[number]
    
    game_dealy_data = {}

    # game_dealy_data['packetsLost'] = pkt_loss_data['packetsLost']
    game_dealy_data['rtts'] = rtt_data['rtts']
    game_dealy_data['timeStamp'] = rtt_data['ts']

    video_perform_data = {}

    video_perform_data['jb_delay'] = video_data['jb_delay']
    video_perform_data['max_decode_ms'] = video_data['max_decode_ms']
    video_perform_data['netFps'] = video_data['net_fps']
    video_perform_data['totalBps'] = video_data['total_bps']
    video_perform_data['timeStamp'] = video_data['time_ms']

    len_gd = len(game_dealy_data['timeStamp'])
    len_vp = len(video_perform_data['timeStamp'])

    # print(game_dealy_data['timeStamp'][0], game_dealy_data['timeStamp'][5201])

    ts_gd_min = math.ceil(game_dealy_data['timeStamp'][0])
    ts_gd_max = math.floor(game_dealy_data['timeStamp'][len_gd - 1] - 1)
    ts_vp_min = math.ceil(video_perform_data['timeStamp'][0])
    ts_vp_max = math.floor(video_perform_data['timeStamp'][len_vp - 1] - 1)

    ts_min = max(ts_gd_min, ts_vp_min)
    ts_max = min(ts_gd_max, ts_vp_max)

    # time_zone = pytz.timezone('US/Eastern')
    # dt = datetime.datetime.fromtimestamp(ts_min, time_zone)
    # day_str = dt.strftime('%m-%d')
    # print(day_str)

    filename = 'summary.csv'
    
    with open(path + filename, mode='w', newline="") as fp:

        wt = csv.writer(fp, delimiter=',')
        wt.writerow(['ts', 'rtt', 'bitrate', 'fps', 'jb_delay', 'max_decode_ms'])

        idx_gd = idx_vp = 0
        
        for ts_floor in range(ts_min, ts_max + 1):
            sum_rtt = sum_fps = sum_bitrate = sum_jbdelay = sum_maxdecodems = 0
            cnt_gd = cnt_vp = 0
            
            while math.floor(game_dealy_data['timeStamp'][idx_gd]) < ts_floor:
                idx_gd += 1
            while math.floor(game_dealy_data['timeStamp'][idx_gd]) == ts_floor:
                sum_rtt += game_dealy_data['rtts'][idx_gd]
                cnt_gd += 1
                idx_gd += 1
            
            while math.floor(video_perform_data['timeStamp'][idx_vp]) < ts_floor:
                idx_vp += 1
            while math.floor(video_perform_data['timeStamp'][idx_vp]) == ts_floor:
                sum_fps += video_perform_data['netFps'][idx_vp]
                sum_bitrate += video_perform_data['totalBps'][idx_vp]
                sum_jbdelay += video_perform_data['jb_delay'][idx_vp]
                sum_maxdecodems += video_perform_data['max_decode_ms'][idx_vp]
                cnt_vp += 1
                idx_vp += 1
            
            if cnt_gd == 0 or cnt_vp == 0:
                continue
            
            mean_rtt = sum_rtt / cnt_gd
            mean_fps = sum_fps / cnt_vp
            mean_bitrate = sum_bitrate / cnt_vp
            mean_jbdelay = sum_jbdelay / cnt_vp
            mean_maxdecodems = sum_maxdecodems / cnt_vp

            wt.writerow([ts_floor, mean_rtt, mean_bitrate, mean_fps, mean_jbdelay, mean_maxdecodems])


def day_sum(path):
    folder_name = path.split('\\')[-1]
    folder_name = folder_name.split('_')

    game = folder_name[0]
    platform = folder_name[1]
    month_day = folder_name[-1]

    sum_file_path = f"{path}\summary.csv"
    print(sum_file_path)

    with open(sum_file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        sum_rtt = sum_bitrate = sum_fps = sum_jbdelay = sum_maxdecodems = 0

        for record in csv_reader:
            line_count += 1
            if line_count == 1:
                continue
            # print(record)
            sum_rtt += float(record[1])
            sum_bitrate += float(record[2])
            sum_fps += float(record[3])
            sum_jbdelay += float(record[4])
            sum_maxdecodems += float(record[5])
        
        # subtract first line
        line_count -= 1

        mean_rtt = sum_rtt / line_count
        mean_bitrate = sum_bitrate / line_count
        mean_fps = sum_fps / line_count
        mean_jbdelay = sum_jbdelay / line_count
        mean_maxdecodems = sum_maxdecodems / line_count
    
    return platform, game, month_day, mean_rtt, mean_bitrate, mean_fps, \
        mean_jbdelay, mean_maxdecodems


# def convert_to_csv():

#     with open('json-output/essential_game_delay.json') as f:
#         game_delay_data

#     with open('json-output/essential_video_perform.json') as f:
#         pass



    # video_perform_data['decodeFps'] = video_data['dec_fps']
    # video_perform_data['renderFps'] = video_data['ren_fps']
    # video_perform_data['renderDelay'] = video_data['render_delay_ms']
    # video_perform_data['decodeDelay'] = video_data['decode_delay']
    # video_perform_data['jitterBufferDelay'] = video_data['jb_delay']
    # video_perform_data['maxDecodeDelay'] = video_data['max_decode_ms']
    # video_perform_data['frameDrop'] = video_data['frame_drop']
    # video_perform_data['frameDecode'] = video_data['frames_decoded']
    # video_perform_data['frameRender'] = video_data['frames_rendered']
    # video_perform_data['freezeCount'] = video_data['freeze_count']
    # video_perform_data['height'] = video_data['height']
    # video_perform_data['width'] = video_data['width']