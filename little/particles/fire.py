import PyIgnition


class FXFire(object):
    def __init__(self, game):
        self.game = game
        self.fire = PyIgnition.ParticleEffect(game.screen, (0, 0), (800, 600))
        self.source = self.fire.CreateSource((300, 500), initspeed=2.0, initdirection=90.0, initspeedrandrange=0.1,
                                             initdirectionrandrange=0.5, particlesperframe=3, particlelife=100,
                                             drawtype=PyIgnition.DRAWTYPE_CIRCLE, colour=(255, 200, 100), radius=3.0)
        self.source.CreateParticleKeyframe(10, colour=(200, 50, 20), radius=1.0, length=1)

        self.moving = False
        self.target_coords = None

    @property
    def coords(self):
        return self.source.pos

    @property
    def y(self):
        return self.source.pos[1]

    @property
    def x(self):
        return self.source.pos[0]

    def move(self, start, end):
        self.moving = True
        self.source.SetPos(start)
        self.source.pos = start
        self.target_coords = end

    def update(self):
        # Particle effects
        if self.source.curframe % 30 == 0:
            self.source.ConsolidateKeyframes()
        self.fire.Update()
        self.fire.Redraw()

        if self.moving:
            dx, dy = (self.target_coords[0] - self.x, self.target_coords[1] - self.y)
            stepx, stepy = (dx / 50., dy / 50.)
            self.source.SetPos((self.x + stepx, self.y + stepy))