import React from "react";
import LoadingSpinner from "./components/LoadingSpinner";
import { domainPath } from "../constants/utils";

export const AppContext = React.createContext();

const AppContextProvider = ({ children }) => {
  const [isLoadingSpinner, setLoadingSpinner] = React.useState(false); // check whether app is sending any request, if YES => show loading spinner

  const appContextData = {
    isLoadingSpinner: isLoadingSpinner,
    fetchRequest: async function (
      endpoint,
      method,
      body = null,
      isJSON = true
    ) {
      setLoadingSpinner(true);

      let url = domainPath + '/' + endpoint;
      let info = {
        method: method,
        headers: {
          Authorization: "JWT " + localStorage.getItem('token'),
        },
      };

      if (isJSON) {
        info["headers"]["Content-Type"] = "application/json";
      }

      if (body !== null) {
        info["body"] = body;
      }

      const result = await fetch(url, info)
        .then(async (res) => {
          let data = await res.json();

          if (res.status === 200) {
            return data;
          } else {
            if (data.message) {
              // alert(data.message);
            } else {
              alert("Internal error server");
            }
          }
        })
        .catch((err) =>  {
          // alert("Failed request")
        }
        );

      setLoadingSpinner(false);
      return result;
    },
  };

  return (
    <AppContext.Provider value={appContextData}>
      {isLoadingSpinner ? <LoadingSpinner /> : <></>}
      {children}
    </AppContext.Provider>
  );
};

export default AppContextProvider;
