class Color(dict):
  def __init__(self):
    Colours = {
      "default" : "#FFFFFF",
      "white": "#FFFFFF",
      "black": "#000000",

      "purple" : "#8841d9",
      "deep-purple" : "#240252",
      "light-purple" : "#a766ff",

      "cyan" : "#00ffb2",
      "light-cyan" : "#68ffd1",

      "red" : "#ff1919",
      "light-red" : "#ff6161",

      "blue" : "#0048ff",
      "light-blue" : "#5988ff",
      "deep-blue" : "#000d9c",

      "green" : "#00ff3f",
      "neon-green": "#ACFF12",
      "light-green" : "#52ff7d",
      "deep-green" : "#40b800",

      "orange": "#FF9900",
      "light-orange": "#FF8B6A0",

      "yelow": "#FFF481",

      "pink": "#FF8DF4",
      "deep-pink": "#FF11E7",
    }
    super().__init__(Colours)

  def __getitem__(self, color="default"):
    return self.get(color.lower())

  def getlist(self):
      self = Color()
      color_list = []
      for item, itemname in self.items():
          color_list.append(item)
      return color_list