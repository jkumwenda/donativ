import { StyleSheet } from "react-native";

export const globalStyles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#F4EFF2",
    marginTop: 40,
  },
  tabTitle: { fontFamily: "nunito-black", fontSize: 16 },
  tabText: { fontFamily: "nunito-regular", fontSize: 14 },
  paragraph: { marginVertical: 8 },
  btn: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    padding: 4,
    borderRadius: 15,
    backgroundColor: "#B21F5E",
    paddingHorizontal: 10,
    color: "#FFF",
    fontWeight: 600,
    padding: 15,
    marginVertical: 4,
  },

  btnIcon: { color: "#FFF" },
  btnText: {
    color: "#FFF",
    marginLeft: 8,
    fontFamily: "nunito-bold",
    fontSize: 16,
  },
  btnTextNoIcon: {
    color: "#FFF",
    fontFamily: "nunito-bold",
    fontSize: 16,
  },
  pageTitle: { fontFamily: "nunito-bold", fontSize: 18, color: "#333" },
  pageTitleSmall: {
    fontFamily: "nunito-bold",
    fontSize: 16,
    padding: 10,
    color: "#333",
  },
  logo: {
    width: 180,
    height: 40,
  },
  logoContainer: { flexDirection: "row", justifyContent: "center" },

  textInput: {
    borderStyle: "solid",
    borderColor: "#ccc",
    borderWidth: 1,
    marginVertical: 8,
    borderRadius: 15,
    paddingHorizontal: 20,
    paddingVertical: 8,
  },
  flexContainer: {
    flex: 1,
    justifyContent: "center",
    paddingTop: 20,
    backgroundColor: "#F4EFF2",
    margin: 20,
  },
  formWrap: {
    backgroundColor: "#FFF",
    padding: 20,
    borderRadius: 20,
    elevation: 0.4, // Adjust the elevation to control the shadow depth
  },
  campaingsContainer: {
    flex: 1,
    backgroundColor: "#2C6695",
  },
  searchBar: {
    padding: 20,
  },
  arcTab: {
    flex: 1,
    padding: 20,
    backgroundColor: "#F4EFF2",
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
});
