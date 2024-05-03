import React from "react";
import * as Font from "expo-font";
import Home from "./src/screens/home";
import Navigator from "./src/routes/Navigation";

let getFonts = {
  "nunito-regular": require("./assets/fonts/Nunito/Nunito-Regular.ttf"),
  "nunito-bold": require("./assets/fonts/Nunito/Nunito-Bold.ttf"),
  "nunito-black": require("./assets/fonts/Nunito/Nunito-Black.ttf"),
  "nunito-light": require("./assets/fonts/Nunito/Nunito-Light.ttf"),
};

export default class App extends React.Component {
  state = {
    fontsLoaded: false,
  };

  async _loadFontsAsync() {
    await Font.loadAsync(getFonts);
    this.setState({ fontsLoaded: true });
  }

  componentDidMount() {
    this._loadFontsAsync();
  }

  render() {
    if (!this.state.fontsLoaded) {
      return null;
    }

    return <Navigator />;
  }
}
