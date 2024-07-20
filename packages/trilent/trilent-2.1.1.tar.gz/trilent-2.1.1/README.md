## Trilent
A new UI framework for python! Full Documenation coming soon.

## Features
# Animations
```python
import trilent as t

window = t.Window()

# Setup

button = t.Button(window, text='I am a Button!')
button.place(100, 100)

# Animate
button.animate(button_color='lime', time=1) # Animate its color slowly to lime, In 1 second.

window.run()
```

