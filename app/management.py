def counting_table(time_map, data):
  starttime_list = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
  endtime_list = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
  # key = 요일
  for key in data:
    # 시작 시간, 끝 시간 가져오기
    for classtime in data[key]:
      start_time, end_time = classtime.split('-')
      start_idx = starttime_list.index(float(start_time))
      end_idx = endtime_list.index(float(end_time))
      
      for idx in range(start_idx, end_idx+1):
        time_map[key][idx] += 1
  
  return time_map

def time_mapping():
  mapping_table = {
    '월':{},
    '화':{},
    '수':{},
    '목':{},
    '금':{}
  }

  for daytime in mapping_table:
    for idx in range(12):
      mapping_table[daytime][idx] = 0
  
  return mapping_table

def find_minimum(mapped):
  minimum = 9999

  for key in mapped:
    for time in mapped[key]:
      if mapped[key][time] < minimum:
        minimum = mapped[key][time]

  return minimum

def check(target_list):
  # 배열의 길이가 1인 경우 true
  if len(target_list) == 1:
    return True
  
  for idx in range(len(target_list) - 1):
    first_end = target_list[idx].split('-')[1]
    second_start = target_list[idx+1].split('-')[0]

    if first_end == second_start:
      return False
  
  return True

def connect(time_list):
  if check(time_list):
    return time_list
  
  for idx in range(len(time_list) - 1):
    first_end = time_list[idx].split('-')[1]
    second_start = time_list[idx + 1].split('-')[0]

    if first_end == second_start:
      time_list[idx] = time_list[idx].split('-')[0] + '-' + time_list[idx+1].split('-')[1]
      del time_list[idx + 1]
      break
  connect(time_list)

def connect_time(minimum_table):
  for key in minimum_table:
    connect(minimum_table[key])
  return minimum_table

def filter_under_fifteen(unfiltered_list):
  for key in unfiltered_list:
    unfiltered_list[key] = [x for x in unfiltered_list[key] if float(x.split('-')[1]) - float(x.split('-')[0]) > 0.25]

  return unfiltered_list

# mapped : 요일별로 해당하는 수업 개수 counting한 dictionary.
def construct_table(mapped):
  starttime_list = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
  endtime_list = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
  minimum_table = {
    '월':[],
    '화':[],
    '수':[],
    '목':[],
    '금':[]
  }

  # minimum 값을 가져온 후, 그 값에 해당하는 시간표만 mapping.
  minimum = find_minimum(mapped)

  for daytime in minimum_table:
    for idx in range(12):
      if mapped[daytime][idx] == minimum:
        minimum_table[daytime].append(f'{starttime_list[idx]}-{endtime_list[idx]}')
  
  # 연결된 시간 잇기
  connected_table = connect_time(minimum_table)
  filtered_table = filter_under_fifteen(connected_table)

  return filtered_table, minimum

def first_person(data):
  time_map = time_mapping()
  mapped = counting_table(time_map, data)
  output = construct_table(mapped)

  return output

def filter_table(meets):
  time_map = time_mapping()
  participants = []
  for person in meets:
    participants.append(person)
    mapped = counting_table(time_map, meets[person])
  output, minimum = construct_table(mapped)

  return output, participants, minimum
  