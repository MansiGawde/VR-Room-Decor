import pygame

def draw_button(screen, text, x, y, w, h):
    pygame.draw.rect(screen, (50,50,50), (x,y,w,h))
    font = pygame.font.SysFont(None, 25)
    label = font.render(text, True, (255,255,255))
    screen.blit(label, (x+10, y+10))

def check_click(pos, x, y, w, h):
    if x < pos[0] < x+w and y < pos[1] < y+h:
        return True
    return False