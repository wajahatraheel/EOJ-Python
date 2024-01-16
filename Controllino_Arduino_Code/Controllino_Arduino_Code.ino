
#include <Controllino.h> /* Usage of CONTROLLINO library allows you to use CONTROLLINO_xx aliases in your sketch. */
#include <Ethernet.h>

//Developed by WRA.
//DEFIND THE CONTROLLER BEFORE UPLOADING INTO CONTROLLER
// The controller value can be MEGA or MAXI or MINI
//===================================================
String controller = "MEGA";
//===================================================


struct messages {
  String pc_message = "";
  String operation;
  String pin_selection;
  String pwm_or_io;
  int output_value;
  int pin_number = 0;
  String message_to_client = "";
  int msg_length = 0;
  int port_number = 0;
  String analoge_or_digital_read = "";
  int error_state = 0;
  String output_state = "";
};
const int set_delay = 50;  //delay value to get inputfeedback after setting output [ms]
messages client_message;
char c;
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 127, 11);
byte subnet[] = { 255, 255, 0, 0 };
EthernetServer server(100);
EthernetClient client;

// the setup function runs once when you press reset (CONTROLLINO RST button) or connect the CONTROLLINO to the PC
void setup() {
  //SETUP OUTPUT AND INPUT PINS
  //Serial.begin(115200);
  Ethernet.begin(mac, ip, subnet);
  server.begin();
}

void Read_PC_message() {


  if (client.available() > 0) {
    // read the incoming byte:

    while (client.available())  //While loop for serial data storage to character array.
    {
      delay(1);  //delay to allow byte to arrive in input buffer ms
      c = client.read();
      client_message.pc_message += c;
    }
    c = "";
  }
}

void port_map_output() {
  if (controller == 'MEGA') {


    // Assign the values of internal port number to given user port number.
    if (client_message.pin_selection[0] == 'D')  // D for Digital
    {


      if (client_message.pin_number >= 0 && client_message.pin_number <= 23) {


        if (client_message.pin_number >= 0 && client_message.pin_number <= 11)  //D0 to D11 Mapping ( Starts with 2-13)
        {
          client_message.port_number = client_message.pin_number + 2;
        }

        if (client_message.pin_number >= 12 && client_message.pin_number <= 19) {
          client_message.port_number = client_message.pin_number + 30;  // port deci num starts with 42-49 (D12-D19)
        }

        if (client_message.pin_number >= 20 && client_message.pin_number <= 23) {
          client_message.port_number = client_message.pin_number + 57;  // port deci num starts with 77-80 (D20-D23)
        }
        client_message.error_state = 0;

      } else {
        client_message.error_state = 1;
      }
    }

    if (client_message.pin_selection[0] == 'R')  // For Relay OUTPUT
    {
      if (client_message.pin_number >= 0 && client_message.pin_number <= 15) {
        client_message.port_number = client_message.pin_number + 22;  //Mapping Relay port from 22-37 (R0-R15)
        client_message.error_state = 0;
      } else {
        client_message.error_state = 1;
      }
    }
  }
  if (controller == 'MAXI')  // Code not tested on  MAXI(10.1.2024)
  {
    if (client_message.pin_selection[0] == 'D')  // D for Digital
    {
      if (client_message.pin_number >= 0 && client_message.pin_number <= 11)  //D0 to D11 Mapping ( Starts with 2-13)
      {
        client_message.port_number = client_message.pin_number + 2;
      }
    }
    if (client_message.pin_selection[0] == 'R')  // For Relay OUTPUT
    {
      client_message.port_number = client_message.pin_number + 22;  //Mapping Relay port from 22-37 (R0-R15)
    }
  }
  if (controller == 'MINI')  //todo: TEST THE CODE ON MINI: ALSO MAP THE PORTS FOR RELAY OUTPUTS:
  {
    if (client_message.pin_selection[0] == 'D')  // D for Digital
    {
      if (client_message.pin_number >= 0 && client_message.pin_number <= 7)  //D0 to D7 Mapping (MINI - Controllino) ( Starts with 2-13)
      {
        client_message.port_number = client_message.pin_number + 4;
      }
    }
  }
}


char DecodeMessage() {

  //the Function DecodeMessage decodes the telegram. the example of setting D0 from 0 to 1 is SET_D0_IO_1
  // the function makes an array with values{'SET','D0', 'IO','1'}
  // the function also decodes message for get for example, GET_A0_A(For digital analog) or GET_A0_D(For digital input)
  int num_of_underscores = 0;  // for indexing the array special_character_index
  int i = 0;                   // for loop iteration
  int special_character_index[3] = {};
  int msg_length = client_message.pc_message.length();
  msg_length = msg_length + 1;       //including NULL character
  for (i = 0; i <= msg_length; i++)  // Extract Special Character out of Telegram. in this case '_'
  {
    if (client_message.pc_message[i] == '_') {
      special_character_index[num_of_underscores] = i;
      num_of_underscores = 1 + num_of_underscores;
    }
  }


  if (num_of_underscores == 3 || num_of_underscores == 2)  // Checks number of underscores in telegram for SET and GET value.
  {

    client_message.operation = client_message.pc_message.substring(0, special_character_index[0]);
    client_message.pin_selection = client_message.pc_message.substring(special_character_index[0] + 1, special_character_index[1]);

    if (client_message.operation == "SET")  // Case if Message is 'SET'
    {
      client_message.pwm_or_io = client_message.pc_message.substring(special_character_index[1] + 1, special_character_index[2]);
      client_message.output_value = client_message.pc_message.substring(special_character_index[2] + 1, msg_length).toInt();
    }

    else if (client_message.operation == "GET")  // Case if Message is 'GET'
    {
      client_message.analoge_or_digital_read = client_message.pc_message.substring(special_character_index[1] + 1, msg_length);
    } else {
      client_message.error_state = 1;  // set get command error
    }



    client_message.pin_number = client_message.pin_selection.substring(1, client_message.pin_selection.length()).toInt();
    client_message.pc_message = "";

  } else {
    client_message.error_state = 1;  // number of underscores are high or low in telegram
  }
}
void OutputControl() {


  // =================FUNCTION PORT MAP OUTPUT=======================
  port_map_output();  // maps the port first. assign the value to ports.
  //======================= ======================= ===================


  if (client_message.error_state == 0) {

    if (client_message.pwm_or_io == "IO")  //Checks if IO is in telegram from the client.
    {

      digitalWrite(client_message.port_number, client_message.output_value);
      delay(50);
      if (client_message.pin_selection[0] == 'D') {
        client.println(digitalRead(client_message.port_number));  // output acknowledge message to client
      }
      if (client_message.pin_selection[0] == 'R') {
        client.println(client_message.output_value);
      }
    }

    if (client_message.pwm_or_io == "PWM") {
      analogWrite(client_message.port_number, client_message.output_value);
      delay(50);
      client.println(client_message.output_value);  // output acknowledge message to client
    }
  }
  if (client_message.error_state == 1) {
    client.println("-1");
  }
}

void port_map_input() {

  if (client_message.pin_selection[0] == 'A') {
    if (controller == 'MEGA') {

      if (client_message.pin_number >= 0 && client_message.pin_number <= 15)  //A0 to A15 Mapping (Starts with 54-69)
      {
        client_message.port_number = client_message.pin_number + 54;
      } else {
        client_message.error_state = 1;
      }
    }
  }
}


void InputControl() {

  port_map_input();

  if (client_message.error_state == 0) {
    if (client_message.analoge_or_digital_read == "D") {
      client.println(digitalRead(client_message.port_number));
      delay(1);
    }

    if (client_message.analoge_or_digital_read == "A") {
      client.println(analogRead(client_message.port_number));
      delay(1);
    }
  } else {
    client.println("-1");
  }
}


//==============================================MAIN LOOP===================================================================
void loop()

{
  client = server.available();
  if (client) {

    Read_PC_message();
    if (client_message.pc_message != "") {
      DecodeMessage();
      if (client_message.operation == "SET") {
        OutputControl();
      }

      if (client_message.operation == "GET") {

        InputControl();
      }

      client_message.pc_message = "";
      client_message.pin_number = 0;
      client_message.operation = "";
      client_message.pin_selection = "";
      client_message.pwm_or_io = "";
      client_message.output_value = "";
      client_message.message_to_client = "";
      client_message.error_state = 0;

      if (client_message.pc_message == "") {
        client_message.pc_message = "";
      }
    }
  }
}
