def solution(arr):
    answer = []
    
    for idx, i in enumerate(arr):
        if idx == 0:
            answer.append(i)
        elif i != answer[-1]:
            answer.append(i)
        
    return answer