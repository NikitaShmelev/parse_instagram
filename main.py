
from data import crefentials
from user import User
import time

def main() -> None:
    users = User.get_users()

    if User.authenticate(crefentials):
        for user in users:
            user.open_profile()
            user.parse_followers()
            # user.parse_following()
            # time.sleep(10)

        pass





if __name__ == "__main__":
    main()

