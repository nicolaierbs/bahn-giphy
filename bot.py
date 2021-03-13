import gifted


scenes = ['landscape-winter']
# scenes = ['landscape-summer', 'landscape-winter']
trains = ['bahn_angela']
# trains = ['bahn_angela', 'ice_comic', 'rb_vbb', 're_vbb', 'sbahn_vbb']

for scene in scenes:
    for train in trains:
        print(gifted.create(scene=scene, train=train, num_frames=50))
