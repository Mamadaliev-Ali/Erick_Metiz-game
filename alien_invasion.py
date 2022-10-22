import sys
from time import sleep
import pygame

from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Billet
from alien import Alien



class AlienInvasion:
    """Создает игровые ресурсы"""

    def __init__(self):
        pygame.init()
        self.settings = Settings()
        # Объект присвоенный self.screen наз. поверхностью (surface)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        pygame.display.set_icon(pygame.image.load("image/sssss.bmp"))
        self.stats = GameStats(self)
        self.ship = Ship(self.screen)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet_()



    def run_game(self):
        """Запуск основного цикла игры"""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self.bullets.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        # Отслеживания событий клавиатуры и мыши 0.09
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keyDown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyUp_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Запускает игру при нажатии на кнопку"""
        if self.play_button.rect.collidepoint(mouse_pos):
            # Сброс игровой статистики
            self.stats.reset_stats()
            self.stats.game_active == True

            # очистка списков пришельца и снарядов
            self.aliens.empty()
            self.bullets.empty()

            # Создание нового флота
            self._create_fleet_()
            self.ship.center_ship()

    def _check_keyDown_events(self, event):
        """Реагирует на нажатие клавиш"""
        if event.key == pygame.K_UP:
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = True
        elif event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_q:
            sys.exit()

    def _check_keyUp_events(self, event):
        """Реагирует на отпускание клавиш"""""
        if event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False
        elif event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_alien_bottom(self):
        """Проверка, добрались ли пришельцы до нижнего края """
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _ship_hit(self):
        """Обрабатывает столкновение корабля и пришельца"""
        if self.stats.ships_left > 0:
            # уменьшение ship_left
            self.stats.ships_left -= 1
            # пауза
            sleep(0.5)
        else:
            self.stats.game_active = False

        # очистка списков пришельцев и снарядов
        self.aliens.empty()
        self.bullets.empty()

        # Создание нового флота и размещение корабля по центру
        self._create_fleet_()
        self.ship.center_ship()

        # Пауза
        sleep(0.5)

    def _fire_bullet(self):
        """Создание нового снаряда и включение его в группу bullets"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Billet(self)
            self.bullets.add(new_bullet)

    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()

        # Проверка Коллизии "пришелец - корабль"
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Проверка, добрались ли пришельцы до нижнего края
        self._check_alien_bottom()

    def _update_bullets(self):
        """Обновляет позиции снаряда и уничтожает старые снаряды"""
        # Обновление позиции снаряда
        self.bullets.update()

        # Удаление снарядов, вышедших за край экрана
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Обработка коллизии снарядов с пришельцами"""
        # Удаление снарядов и пришельцев, участвующих в коллизии
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        if not self.aliens:
            # Уничтожение существующий зарядов и создание нового флота
            self.bullets.empty()
            self._create_fleet_()

    def _create_alien(self, alien_number, row_number):
        # Создание пришельца и размещение его в ряду
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Реагирует на достижение пришельца края экрана"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self.change_fleet_direction()
                break

    def change_fleet_direction(self):
        """Опускать весь флот и менять направление флота"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _create_fleet_(self):
        """Создание флота"""
        # Создание пришельца и вычисления количество пришельцев в ряду.
        # Интервал между соседними пришельцами равен ширине пришельца.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_spase_x = self.settings.screen_width - (2 * alien_width)
        number_alien_x = available_spase_x // (2 * alien_width)

        """Определят количество рядов, помещающихся на экране"""
        ship_height = self.ship.rect.height
        available_spase_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = available_spase_y // (2 * alien_height)

        # Создание флота вторжения
        for row_number in range(number_rows):
            for alien_number in range(number_alien_x):
                self._create_alien(alien_number, row_number)

    def _update_screen(self):
        # При каждом переходе цикла перерисовывается экран.
        self.screen.fill(self.settings.bg_color)
        self.ship.blit_me()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
