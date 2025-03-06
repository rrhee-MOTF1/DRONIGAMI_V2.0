function getWeather(lat, long) {
    let timeZoneValue = new Date().getTimezoneOffset() / 60;
    let requestPoint = new XMLHttpRequest();
    let requestPointUrl = "https://api.checkwx.com/metar/lat/" + lat + "/lon/" + long + "/decoded"
    requestPoint.open("GET", requestPointUrl,false);
    requestPoint.setRequestHeader("X-API-Key", "a2dd4a13ad404da8b26d6b42ff");
    requestPoint.send();
    if (requestPoint.status != 200) {
        return requestPoint.status
    } else {
        let METARResponse = JSON.parse(requestPoint.responseText);
        let returnArray = METARResponse.data[0];
        let returnValue = "";
        let observedDate = new Date(returnArray.observed);
        let observedDateAdjusted = new Date(observedDate.setHours(observedDate.getHours() - timeZoneValue));
        returnValue += returnArray.icao + " - " + returnArray.observed + "Z (" + observedDateAdjusted.toString() + ")<br>" +
            returnArray.station.name + " (type: " + returnArray.station.type + ") - " + returnArray.station.location;
        returnValue += "<br>Station is located " + returnArray.position.distance.miles + " miles at " + returnArray.position.bearing.from +
            " degrees relative to the mission location";
        returnValue += "<br><br>METAR: " + returnArray.raw_text;
        returnValue += "<br><br>PARSED:<br>On " + observedDateAdjusted.toString() + " from " + returnArray.icao + ",";
        if (returnArray.wind) {
            returnValue += "<br>WINDS blowing to the station from a point " + returnArray.wind.degrees + " degrees relative to the station at " + returnArray.wind.speed_mph + " mph";
            if (returnArray.wind.gust_mph) {
                returnValue += "<br>GUSTS may reach " + returnArray.wind.gust_mph + " mph";
            }
        }
        if (returnArray.visibility) {
            returnValue += "<br>VISIBILITY is " + returnArray.visibility.miles + " miles";
        }
        if (returnArray.conditions) {
            returnValue += "<br>SKY CONDITIONS: ";
            for (let conditionArray in returnArray.conditions) {
                returnValue += returnArray.conditions[conditionArray].text + " ";
            }
        }
        if (returnArray.snow || returnArray.rain) {
            returnValue += "<br>PRECIPITATION: ";
            if (returnArray.rain) {
                if (returnArray.rain.inches) {
                    returnValue += "RAIN - " + returnArray.rain.inches + " inches";
                }
            }
            if (returnArray.snow) {
                if (returnArray.snow.inches) {
                    returnValue += "SNOW - " + returnArray.snow.inches + " inches";
                }
            }
        }
        if (returnArray.ceiling) {
            returnValue += "<br>CEILING is at " + returnArray.ceiling.feet + " feet AGL";
        }
        if (returnArray.clouds) {
            returnValue += "<br>CLOUDS: ";
            for (let cloudArray in returnArray.clouds) {
                returnValue += " " + returnArray.clouds[cloudArray].text + " ";
                    if (returnArray.clouds[cloudArray].base_feet_agl) {
                        returnValue += "at " + returnArray.clouds[cloudArray].base_feet_agl + " ft AGL at base ";
                }
            }
        }
        if (returnArray.temperature) {
            returnValue += "<br>TEMPERATURE is " + returnArray.temperature.celsius + " deg C (" + returnArray.temperature.fahrenheit + " deg F)";
        }
        if (returnArray.dewpoint) {
            returnValue += "<br>DEWPOINT is " + returnArray.dewpoint.celsius + " deg C (" + returnArray.dewpoint.fahrenheit + " deg F)";
        }
        if (returnArray.humidity) {
            returnValue += "<br>HUMIDITY is " + returnArray.humidity.percent + "%";
        }
        if (returnArray.barometer) {
            returnValue += "<br>ALITMETER (PRESSURE) is " + returnArray.barometer.hg + " inches";
        }
        returnValue += "<br><br>Additional remarks may be designated by RMK. Check METAR text above for remarks";
        return returnValue;
    }
}

function getTAF(lat, long) {
    var timeZoneValue = new Date().getTimezoneOffset()/60;	

    const pointApiUrl = "https://api.checkwx.com/taf/lat/";

	const requestPoint = new XMLHttpRequest();
	const requestPointUrl = pointApiUrl + lat + "/lon/" + long + "/decoded";

	requestPoint.open("GET", requestPointUrl, false);
		requestPoint.setRequestHeader("X-API-Key", "a2dd4a13ad404da8b26d6b42ff")
		requestPoint.send();

    if (requestPoint.status != 200){
		return requestPoint.status;
	} else {
		const METARResponse = JSON.parse(requestPoint.responseText);
		const returnData = METARResponse.data[0];
		const returnForecast = returnData.forecast;
		let returnValue = returnData.icao + " || " + returnData.station.name + " (type: " + returnData.station.type + ") " + " - " + returnData.station.location;
		returnValue += "<br>" + returnData.position.distance.miles + " miles at " + returnData.position.bearing.from + " degrees relative to the mission location"; 
		returnValue += "<br><br>TAF: " + returnData.raw_text;
		let issueDate = new Date(returnData.timestamp.issued)
		let issueDateAdjust = new Date(issueDate.setHours(issueDate.getHours() - timeZoneValue))
		let fromDate = new Date(returnData.timestamp.from)
		let fromDateAdjust = new Date(fromDate.setHours(fromDate.getHours() - timeZoneValue))
		let toDate = new Date(returnData.timestamp.to)
		let toDateAdjust = new Date(toDate.setHours(toDate.getHours() - timeZoneValue))
		returnValue += "<br><br>ALL FOLLOWING TIMES ARE ADJUSTED TO THE CURRENT TIME ZONE<br><br>PARSED:<br>----Issued on " + issueDateAdjust.toString().substring(4,16) + " || Valid from " + fromDateAdjust.toString().substring(4,10) + fromDateAdjust.toString().substring(15,21) + " to " + toDateAdjust.toString().substring(4,10) + toDateAdjust.toString().substring(15,21);
		for (let array of returnForecast) {
			let string_var = "";
			let fromForecastDate = new Date(array.timestamp.from)
			let fromForecastDateAdjust = new Date(fromForecastDate.setHours(fromForecastDate.getHours() - timeZoneValue))
			let toForecastDate = new Date(array.timestamp.to)
			let toForecastDateAdjust = new Date(toForecastDate.setHours(toForecastDate.getHours() - timeZoneValue))
			string_var += fromForecastDateAdjust.toString().substring(8,10) + fromForecastDateAdjust.toString().substring(15,21) + " to " + toForecastDateAdjust.toString().substring(8,10) + toForecastDateAdjust.toString().substring(15,21) + "...";
			if (array.change) {
				string_var += array.change.indicator.desc + " || ";
			}
			if (array.wind) {
				string_var += "WIND- Blowing from " + array.wind.degrees + " degrees at " + array.wind.speed_mph + " mph || ";
				if (array.wind.gust_mph) {
					string_var += "GUSTS- Up to " + array.wind.gust_mph + " mph || "
				}
			}
			if (array.visibility) {
				string_var += "VISIBILITY- " + array.visibility.miles + " miles || ";
			}
			if (array.conditions) {
				string_var += "CONDITIONS-";
				for (let condition_array in array.conditions) {
					string_var += " " + array.conditions[condition_array].text + " ";
				}
				string_var += "|| "
			}
			if (array.clouds) {
				string_var += "CLOUDS- ";
				for (let cloudArray in array.clouds) {
					string_var += array.clouds[cloudArray].text + " ";
					if (array.clouds[cloudArray].feet) {
						string_var += "at " + array.clouds[cloudArray].feet + " ft AGL ";
					}
				}
				string_var += "|| "
			}
			if (array.icing) {
				string_var += "ICING-";
				for (let icingArray in array.icing) {
					string_var += " Intensity: " + array.icing[icingArray].intensity.desc + " from " + array.icing[icingArray].minimum.feet + " to " + array.icing[icingArray].maximum.feet + "ft AGL "
				}
				string_var += "|| "
			}
			if (array.turbulence) {
				string_var += "TURBULENCE- " + array.turbulence.intensity.desc + " from " + array.turbulence.minimum.feet + " to " + array.turbulence.maximum.feet + " ft AGL ||"
			}
			returnValue += "<br>----" + string_var
				
		}
		return returnValue
	}
}