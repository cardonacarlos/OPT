from tkinter import *

root = Tk()
Label(root, text = "Childs First name").grid(row = 0, sticky = W)
Label(root, text = "Childs Surname").grid(row = 1, sticky = W)
Label(root, text = "Childs Year of Birth").grid(row = 2, sticky = W)
Label(root, text = "Childs Month of Birth").grid(row = 3, sticky = W)
Label(root, text = "Childs Day of Birth").grid(row = 4, sticky = W)

Fname = Entry(root)
Sname = Entry(root)
x = Entry(root)
y = Entry(root)
z = Entry(root)


Fname.grid(row = 0, column = 1)
Sname.grid(row = 1, column = 1)
x.grid(row = 3, column = 1)
y.grid(row = 2, column = 1)
z.grid(row = 4, column = 1)

def getInput():

    a = Fname.get()
    b = Sname.get()
    c = x.get()
    d = y.get()
    e = z.get()
    root.destroy()

    global params
    params = [a,b,c,d,e]


Button(root, text = "submit",
           command = getInput).grid(row = 5, sticky = W)
mainloop()