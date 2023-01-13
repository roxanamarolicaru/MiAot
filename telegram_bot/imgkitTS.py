import imgkit

options = {
    'format': 'png',
    'crop-w': '450',
    'encoding': "UTF-8",
    'javascript-delay': '1000'
}

def retrievePlot(chat_ID,index):
    return imgkit.from_url('https://thingspeak.com/channels/1277474/charts/'+index+'?bgcolor=%23ffffff&color=%23d62020&dynamic=true&results=60&type=line&update=15', str(chat_ID)+'_'+index+'_'+'tmp.jpg', options=options)
