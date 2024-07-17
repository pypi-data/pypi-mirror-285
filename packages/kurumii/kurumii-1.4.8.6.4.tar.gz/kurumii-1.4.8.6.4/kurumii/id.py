import random
import datetime

def generateId(amount:int):
    if amount <=0 or type(amount) != int:
        print("integers and positive numbers only!")
        raise ValueError()
    temp = []
    for i in range(0,amount+1):
        add = random.randint(0,9)
        temp.append(str(add))
    date = datetime.datetime.utcnow()
    temp_ = str(temp).replace(' ','').replace(',','').replace("'","").replace("[","").replace("]","")
    out = str(date) + temp_
    out_= out.replace("-","").replace(' ','').replace(':','').replace('.','')
    return(str(out_))

def splitStringAt50Percent(input_string):
    middle_index = len(input_string) // 2
    first_half = input_string[:middle_index]
    second_half = input_string[middle_index:]
    
    return first_half, second_half

def generateTextId(amount:int):
    if amount<=0 or type(amount) != int:
        print("integers and positive numbers only!")
        raise ValueError
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890ß?=)(/&%$§!)-.,^°\_:;#'+*~´`<>|"
    temp = []
    for i in range(0,amount+1):
        
        temp.append(random.choice(letters))
    time = datetime.datetime.utcnow()
    temp_ = str(temp).replace(' ','').replace(',','').replace("'","").replace("[","").replace("]","")
    time_ = str(time).replace("-","").replace(' ','').replace(':','').replace('.','')
    temp1,temp2 = splitStringAt50Percent(temp_)
    out = temp1 + time_ + temp2
    return(out)