from pywinauto import Application
from flask import Flask, request, jsonify
import time


app = Flask(__name__)



def reset_client(serial_number: str):  
      
     try:

         # IP-Adresse des Clients prüfen
        client_ip = request.remote_addr
        allowed_ips = ["192.168.1.185","185.237.66.107"]  # IP-Adresse, die erlaubt ist
        if client_ip not in allowed_ips:
            return jsonify({
                "message": "Zugriff nicht erlaubt."
            }), 403
            
        app_ui = Application(backend="uia").start(
            r"C:\Program Files (x86)\DimSport\DSManager\DSMANAGER.EXE"
        )
        app_ui = Application(backend="uia").connect(
            title="DS Manager - 2.0.9.15", timeout=100)
        
        dlg = app_ui.window(title="DS Manager - 2.0.9.15")
        dlg.child_window(title="My Genius Manager", control_type="Button").click_input()
        time.sleep(5)

        dlg2 = app_ui.window(title="DS Manager - MyGenius Manager - 2.0.9.15")
        dlg2.menu_select("Datei->Reset Client…")
        time.sleep(5)

        dlg3 = app_ui.window(title="DS Manager - MyGenius Manager - Client zurücksetzen")
        dlg3.wait("visible", timeout=10)
        dlg3.print_control_identifiers()    
        
        return {"status": 200, "message": "Erfolgreich abgeschlossen"}

     except Exception as e:
        # Jede Exception abfangen und als Fehler zurückgeben
        print(e)
        return {"status": 200, "message": str(e)}
        #return {"status": 200, "message": "Server Fehler"}


def change_brand(serial_number: str, vehicle_brand: str):
#return {"status": 200, "message": "Server Fehler"}
    
    try:
        app_ui = Application(backend="uia").start(
            r"C:\Program Files (x86)\DimSport\DSManager\DSMANAGER.EXE"
        )
        app_ui = Application(backend="uia").connect(
            title="DS Manager - 2.0.9.16", timeout=10
        )

        dlg = app_ui.window(title="DS Manager - 2.0.9.16")
        dlg.child_window(title="My Genius Manager", control_type="Button").click_input()
        time.sleep(5)

        dlg2 = app_ui.window(title="DS Manager - MyGenius Manager - 2.0.9.16")
        dlg2.wait("visible", timeout=10)

        dlg2.child_window(
            title="MyGenius Remote Geräte", control_type="Button"
        ).click_input()

        # Seriennummer setzen
        textbox = dlg2.child_window(auto_id="textBoxSerialFilter", control_type="Edit")
        textbox.set_text(serial_number)

        try:
            # Marke auswählen
            combo = dlg2.child_window(auto_id="cmdABLFamRemote", control_type="ComboBox")
            combo.type_keys(f"{vehicle_brand}{{ENTER}}", pause=0, with_spaces=True, set_foreground=True)
        except Exception as e:
        # Jede Exception abfangen und als Fehler zurückgeben
            time.sleep(3)
            app_ui.kill()
            return {"status": 200, "message": "Seriennummer nicht gefunden oder Marke nicht bekannt"}


        btn = dlg2.child_window(auto_id="btnUploadABLRemote", control_type="Button")
        btn.wait("enabled", timeout=5)
        btn.click_input()  # Falls wirklich geklickt werden soll


        try:
            time.sleep(1)
            dlg3 = app_ui.window(title="Info")
            #dlg3.print_control_identifiers()
            
            btnInfo = dlg3.child_window(auto_id="button3", control_type="Button")
            btnInfo.wait("enabled", timeout=5)
            btnInfo.click_input()

        except Exception as e:
        # Jede Exception abfangen und als Fehler zurückgeben
            time.sleep(3)
            app_ui.kill()
            return {"status": 200, "message": "Keine kostenlose Freigabe möglich"}
        

        time.sleep(3)
        app_ui.kill()

        return {"status": 200, "message": "Erfolgreich abgeschlossen"}

    except Exception as e:
        # Jede Exception abfangen und als Fehler zurückgeben
        print (e)
        return {"status": 200, "message": "Server Fehler"}


#Route für Changebrand RESET
@app.route("/myg/reset-client/", methods=["POST"])
def reset_client_handler():
    try:   
         # IP-Adresse des Clients prüfen
        client_ip = request.remote_addr
        allowed_ips = ["192.168.1.1","185.237.66.107"]  # IP-Adresse, die erlaubt ist
        if client_ip not in allowed_ips:
            return jsonify({
                "message": "Zugriff nicht erlaubt."
            }), 403
        
          # JSON aus dem Request-Body lesen
        data = request.get_json(force=True)
        print (data)

        # Felder abrufen
        mygSerialNumber = data.get("serialNumber")

        result =  reset_client(mygSerialNumber)
        status = result.get("status", 400)
        return jsonify(result), status
       
    except Exception as e:
        # Alle unerwarteten Fehler abfangen
        return jsonify({
            "message": str(e)
        }), 500    

#Route für Changebrand POST
@app.route("/myg/changebrand/", methods=["POST"])
def changebrand_handler():
    try:
          # IP-Adresse des Clients prüfen
        client_ip = request.remote_addr
        allowed_ips = ["192.168.1.1","192.168.1.185","185.237.66.107"]  # IP-Adresse, die erlaubt ist
        if client_ip not in allowed_ips:
            return jsonify({
                "message": "Zugriff nicht erlaubt."
            }), 403


        # JSON aus dem Request-Body lesen
        data = request.get_json(force=True)
        print (data)

        # Felder abrufen
        mygSerialNumber = data.get("serialNumber")
        mygChangeToVehicle = data.get("vehicleBrand")

        # Eingaben prüfen
        if not mygSerialNumber or not mygChangeToVehicle:
            return jsonify({
                "message": "serialNumber und vehicleBrand müssen angegeben werden."
            }), 400
        

        # Seriennummer prüfen (genau 8 Ziffern)
        if not mygSerialNumber.isdigit() or len(mygSerialNumber) != 8:
            return jsonify({
                "message": "serialNumber muss genau 8 Ziffern enthalten."
            }), 400

        # pywinauto-Funktion aufrufen
        result = change_brand(mygSerialNumber, mygChangeToVehicle)
        status = result.get("status", 400)
        return jsonify(result), status

    except Exception as e:
        # Alle unerwarteten Fehler abfangen
        return jsonify({
            "message": str(e)
        }), 500

# Server starten
if __name__ == "__main__":
    # debug=True für automatischen Neustart beim Code-Ändern
    app.run(host="0.0.0.0", port=29000, debug=True)

