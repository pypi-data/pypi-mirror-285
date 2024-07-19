import matplotlib.pyplot as plt

def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in creating plot: {e}")
            fig, ax = plt.subplots()
            ax.set(frame_on=False)
            ax.set_yticks([])
            ax.set_xticks([])
            return fig  # Replace with your actual empty plot logic

    return wrapper