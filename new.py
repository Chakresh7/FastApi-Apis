import csv

with open('text.csv','r') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        print(row)
        
with open('output.csv','w') as f :
    writer = csv.writer(f)
    writer.writerows([['Name','Age','Country'],
                    ['Name','Age','Country'],
                    ['Name','Age','Country']])
    # reader = csv.reader(f)
    # for row in reader:
    #     print(row)
    
with open('output.csv','r') as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)