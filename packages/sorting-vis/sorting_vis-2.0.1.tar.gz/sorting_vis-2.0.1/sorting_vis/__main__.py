from sorting_vis.gui import Home


def start() -> None:
    app = Home()
    app.mainloop()


if __name__ == "__main__":  # this is needed for some reason
    start()
