import time, tdl

class Animation:
    def __init__(self, duration=500):
        self.duration = duration # in ms

    def perform_animation_frame(self, GS, args, frame):
        pass
    
    def run(self, GS, args, duration=None, callback=None):
        if not duration:
            duration = self.duration
        frame = 0
        done = False
        while not done:
            done = self.perform_animation_frame(GS['console'], args, frame)
            tdl.flush()
            frame += 1
            time.sleep(duration*0.001)

        if callback:
            return callback(frame, duration)

class NonBlockingAnimation(Animation):
    def __init__(self, GS, args, duration=500):
        super().__init__(duration)
        GS['animations'].append(self)
        self.args = args

    def run(self, GS, frame, duration=None, callback=None):
        if not duration: duration = self.duration
        done = self.perform_animation_frame(GS['console'], self.args, frame)
        if done: GS['animations'].remove(self)
        time.sleep(duration*0.001)
        
        return done

class FireMissleAnimation(Animation):
    def __init__(self, duration=15):
        super().__init__(duration)

    def perform_animation_frame(self, console, args, frame):
        missle, src, dest = args
        line = tdl.map.bresenham(src[0], src[1], dest[0], dest[1])
        
        console.drawChar(line[frame-1][0], line[frame-1][1], ' ')
        console.drawChar(line[frame][0], line[frame][1], missle.char)
        
        return frame == len(line)-1

