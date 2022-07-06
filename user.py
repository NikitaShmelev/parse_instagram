import time, re, sqlite3
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import webbrowser

from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from data import users_to_parse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class User:
    def __init__(self, name: str) -> None:
        self.username = name
        self.followers = list()
        self.following = list()
        self.__db_name = f"{self.username}_datetime.today().strftime('%Y-%m-%d %H:%M:%S')"

    browser = webdriver.Chrome(ChromeDriverManager().install())

    @staticmethod
    def authenticate(credentials: dict) -> bool:
        """
        Return True if authentication was succesful\n
        Return False if authentication was NOT succesful and raises ERROR
        """
        try:
            User.browser.get('https://instagram.com')
            time.sleep(10)
            User.browser.find_element(by=By.XPATH, value='/html/body/div[4]/div/div/button[2]').click()
            time.sleep(2)

            input_username = User.browser.find_element("name", "username")
            input_password = User.browser.find_element("name", "password")
            input_username.send_keys(credentials['login'])
            time.sleep(2)
            input_password.send_keys(credentials['password'])
            time.sleep(2)
            input_password.send_keys(Keys.ENTER)
            time.sleep(10)

            User.browser.find_element(by=By.XPATH, value='/html/body/div[1]/section/main/div/div/div/section/div/button').click()
            time.sleep(10)

            User.browser.find_element(
                            by=By.XPATH,
                            value='/html/body/div[1]/div/div[1]/div/div[2]'
                                    '/div/div/div[1]/div/div[2]/div/div/div'
                                    '/div/div/div/div/div[3]/button[2]').click()

            time.sleep(10)
            return True

        except Exception as err:
            print(err, 'LOGIN FUCK UP!!!')
            return False

    @staticmethod
    def get_users() -> tuple:
        """Return tuple of User's class objects"""
        return tuple(
                [User(name) for name in users_to_parse]
            )


    def __open_db_connection(self):
        conn = sqlite3.connect("self.__db_name.db") ## add db name generator
        cursor = conn.cursor()
        return conn, cursor

    @staticmethod
    def __insert_follower(conn, cursor, username):
        cursor.execute('INSERT INTO FOLLOWERS (USERNAME) VALUES(?)', (username,))
        conn.commit()


    def __create_table(self):
        conn, cursor = self.__open_db_connection()
        sql ='''CREATE TABLE IF NOT EXISTS FOLLOWERS (
        USERNAME STRING
        )'''
        cursor.execute(sql)
        conn.commit()
        conn.close()


    def parse_followers(self, group='followers', verbose=True) -> None:
        conn, cursor = self.__open_db_connection(f"{self.username}")
        self.__create_table()
        self._open_dialog(self._get_link())
        print('\nGetting {} users…{}'.format(
            self.expected_number,
            '\n' if verbose else ''
        ))

        links = []
        last_user_index = 0
        updated_list = self._get_updated_user_list()
        initial_scrolling_speed = 5
        retry = 2

        # While there are more users scroll and save the results
        while updated_list[last_user_index] is not updated_list[-1] or retry > 0:
            self._scroll(self.users_list_container, initial_scrolling_speed)

            for index, user in enumerate(updated_list):
                if index < last_user_index:
                    continue

                try:
                    link_to_user = user.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    last_user_index = index
                    user_name = link_to_user[26:-1]
                    User.__insert_follower(conn, cursor, user_name)
                    if link_to_user not in links:
                        links.append(link_to_user)
                        if verbose:
                            print(
                                '{0:.2f}% {1:s}'.format(
                                round(index / self.expected_number * 100, 2),
                                link_to_user
                                )
                            )

                except:
                    if (initial_scrolling_speed > 1):
                        initial_scrolling_speed -= 1
                    pass

            updated_list = self._get_updated_user_list()
            if updated_list[last_user_index] is updated_list[-1]:
                retry -= 1

        print('100% Complete')
        del conn, cursor

    def parse_following(self) -> None:
        # print(self._get_link())
        pass
        # User.browser.get(f"https://instagram.com/{self.username}/following/")


    def open_profile(self):
        User.browser.get(f'https://instagram.com/{self.username}')


    def _get_link(self, group='followers'):
        """Return the element linking to the users list dialog."""

        print(f'\nNavigating to {self.username} profile…' )
        User.browser.get(f'https://www.instagram.com/{self.username}/')
        try:
            return WebDriverWait(User.browser, 5).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, group))
            )
        except:
            self._get_link(self.username, group)


    def _open_dialog(self, link):
        """Open a specific dialog and identify the div containing the users
        list."""

        link.click()
        self.expected_number = int(
            re.search('(\d+)', link.text).group(1)
        )
        time.sleep(1)
        self.users_list_container = User.browser.find_element(
            by=By.XPATH,
            value='//div[@role="dialog"]//ul/parent::div'
        )
        print(self.expected_number)
        time.sleep(3)



    def _get_updated_user_list(self):
        """Return all the list items included in the users list."""

        return self.users_list_container.find_elements(By.XPATH, 'ul//li')

    def _scroll(self, element, times = 1):
        """Scroll a specific element one or more times with small delay between
        them."""

        while times > 0:
            User.browser.execute_script(
                'arguments[0].scrollTop = arguments[0].scrollHeight',
                element
            )
            time.sleep(.2)
            times -= 1


