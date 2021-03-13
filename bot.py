import gifted
import bahnconnection


scenes = ['landscape-summer']
# scenes = ['landscape-summer', 'landscape-winter']
trains = ['bahn_angela']
# trains = ['bahn_angela', 'ice_comic', 'rb_vbb', 're_vbb', 'sbahn_vbb']
connections = bahnconnection.connections('Darmstadt', 'Frankfurt')

for scene in scenes:
    for train in trains:
        print(gifted.create(
            scene=scene,
            train=train,
            num_frames=50,
            connections=connections,
            text='#dbregiodatahack21'))
