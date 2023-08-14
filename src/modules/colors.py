class Color(dict):
  def __init__(self):
    Colours = {
      "default" : "#FFFFFF",
      "purple" : "#8841d9",
      "deep-purple" : "#240252",
      "light-purple" : "#a766ff",
      "cyan" : "00ffb2",
      "light-cyan" : "#68ffd1",
      "red" : "#ff3d44",
      "light-red" : "#faa0a3",
      "blue" : "#0022ff",
      "light-blue" : "#5c70f2",
      "deep-blue" : "#020c4f",
      "green" : "#00ff3f",
      "light-green" : "#52ff7d",
      "deep-green" : "#014011",
    }
    super().__init__(Colours)

  def __getitem__(self, color="default"):
    return self.get(color.lower())