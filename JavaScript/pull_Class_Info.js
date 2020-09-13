// Set Global Variables
window.calendar_Add_on_Counter = 0;
window.color_Changing_Time = false;
window.good_Sections = [];
window.filter_Class_Term;
window.num_Overlay = 0;
window.pageState;
window.calendar_Event_Colors = [
  "#FFAA01",   // Orange (First Color Gets Skipped in Line Up)
  "#727cff",   // Blue
  "#f35274",   // Red
  "#e45bf1",   // Purple
  "#13CA91",   // Green
  "#FF8B8B",   // Light Pink
  "#ffc804"    // Yellow
]

function change_Btn_Colors(event_Class_ID_List, class_Code) {
  // After holding for 2 seconds, switch colors
  var delayInMilliseconds = 1250; // Time to Delay in MiliSeconds
  window.color_Changing_Time = true;
  let interval = setInterval(function() {
    // Stop when mouse is up
    if (window.color_Changing_Time === false) {clearInterval(interval); savePageState(); return false;}
    // Get Color
    window.calendar_Add_on_Counter = window.calendar_Add_on_Counter + 1;
    let new_Color = window.calendar_Event_Colors[window.calendar_Add_on_Counter%window.calendar_Event_Colors.length];
    // Change the Color of Events in Calendar
    var changing_Events = document.getElementsByClassName(event_Class_ID_List[0]);
    for (let i = 0; i < changing_Events.length; i++) {
      changing_Event = changing_Events[i]
      changing_Event.style.backgroundColor = new_Color}
    // Change the Color of Events in Class List
    var display_Button = document.getElementsByClassName(event_Class_ID_List[1]);
    var display_Button_Copy = [...display_Button];
    for (var i=display_Button.length-1; i >= 0; i--) {
      if (display_Button[i].innerText === class_Code) {
        display_Button[i].style.backgroundColor = new_Color;}
      }
  }, delayInMilliseconds);
}

function fix_Overlapping_Events(parent, action_Child, stage) {
  // Initialize Variable for the Removing/Adding Process
  var eps = 0.01 // To Ensure that (ex) 2.001 and 2.00 are Note Conidered Overlapping
  window.num_Overlay = 0;
  var descendents = parent.getElementsByTagName('button');
  for (var i = 0; i < descendents.length; ++i) {
      var prev_Child = descendents[i];
      // Find if Overlap Exists (Slice the word 'rem' out of Values)
      var prev_Child_Bottom = parseInt(prev_Child.style.top.slice(0, -3)) + parseInt(prev_Child.style.height.slice(0, -3));
      var action_Child_Bottom = parseInt(action_Child.style.top.slice(0, -3)) + parseInt(action_Child.style.height.slice(0, -3));
      var is_Overlap = !(prev_Child_Bottom < parseInt(action_Child.style.top) + eps ||
                    parseInt(prev_Child.style.top) + eps > action_Child_Bottom);
      // If it Does Fix CSS of Overlapping Elements
      if (is_Overlap) {
        // Calculate New Width to Fit all Elements to be Added
        var old_Width = String(prev_Child.style.width).slice(0, -1);
        var num_Prev = Math.round(100/parseInt(old_Width));
        if (stage==="add") {var new_Width = 100/(num_Prev+1);}
        else if (stage==="remove") {var new_Width = 100/(num_Prev-1);}
        // Change Width of the Element to Fit Column
        prev_Child.style.width = String(new_Width) + "%";
        action_Child.style.width = String(new_Width) + "%";
        // Prevent Overlap by Specifying Margin
        if (stage==="remove" && prev_Child === action_Child) {window.num_Overlay -= 1;}
        prev_Child.style.marginLeft = String(window.num_Overlay*new_Width) + "%";
        action_Child.style.marginLeft = String(100-new_Width) + "%";
        // Keep Track of Number Overlapping (in Section we are Adding)
        window.num_Overlay += 1;
      }
      else {console.log("No Overlap Found");}
  }
}

// Function to Filter Classes Table With Search Bar
function search_Database() {
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("class_Database");
  filter = input.value.toUpperCase();
  table = document.getElementById("class_Table");
  tr = table.getElementsByTagName("tr");
  for (i = 0; i < tr.length; i++) {
      td_Col1 = tr[i].getElementsByTagName("td")[0];
      td_Col3 = tr[i].getElementsByTagName("td")[2];
      if (td_Col1) {
        txtValue_Col1 = td_Col1.textContent || td_Col1.innerText;
        txtValue_Col3 = td_Col3.textContent || td_Col3.innerText;
        // If Input Found in Text, Display it
        if (txtValue_Col1.toUpperCase().indexOf(filter) > -1 || txtValue_Col3.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";}
        else {
          tr[i].style.display = "none";}
    }
  }
}


function get_Time_Info_From_Section(section_Info, section_Number = -1) {
  if (section_Number === -1) {
    for (var section_Key in section_Info) {section_Number = section_Key; break}}
  section_Key = String(("0" + section_Number).slice(-2));
  var start_Time_List = []; var end_Time_List = []; var class_Days_List = [];
  var time_List = section_Info[section_Key]['section_Time']
  for (var i=0; i < time_List.length; i++) {
    time_Element = time_List[i];
    // If No Time Info Present, Say NA
    if (time_Element === "A" || time_Element === "" || time_Element === "NA") {
      start_Time_List.push("NA"); end_Time_List.push("NA"); class_Days_List.push("NA")}
    // Assuming Format: "MW 12:00 - 13:00  -> Get Time Info"
    else {
      // Remove O = Organizational Meeting, S = Saturday, U = Sunday
      class_Days_List.push(time_Element.split(" ")[0].replace("OM","").replace(",","").replace("U","").replace("S",""))
      start_Time_List.push(time_Element.split(" ")[1])
      end_Time_List.push(time_Element.split(" ")[3])}
  }
  console.log("start, end, days list: ", start_Time_List, end_Time_List, class_Days_List)
  return {start_Time_List, end_Time_List, class_Days_List}
}

function get_Loc_Info_From_Section(section_Info, section_Number = -1) {
  if (section_Number === -1) {
    for (var section_Key in section_Info) {section_Number = section_Key; break}}
  section_Key = String(("0" + section_Number).slice(-2));
  class_Location = section_Info[section_Key]['section_Loc']
  if (class_Location === "A" || class_Location === "" || class_Location === " ") {class_Location = "NA";}
  return class_Location
}

// Function to Output Class Details When Class Code is Clicked in Table
function add_Description(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
  // Extract Information for Each Section
  let grading_Scheme = "NA";
  let section_Info = section_Info_Holder[String(window.filter_Class_Term).toLowerCase()]
  for (var section_Key in section_Info) {grading_Scheme = section_Info[section_Key]['section_Grading']; break}
  if (grading_Scheme === "" || grading_Scheme === " ") {grading_Scheme = "NA";}
  var describe_Class = '<hr class="section_Divider Dark-Line mt-4">'
  describe_Class += '<div class="pt-3">'
  describe_Class += '<span class="class_Code_Text">'+class_Code+': </span>'
  describe_Class += '<span class="class_Name_Text">' + class_Name + '</span>'
  describe_Class += "<button id='add_Button_Click' class='add_Button btn btn-outline-danger mb-1')>Add Class</button>"
  describe_Class += '<div class="small_Description_Text">'
  describe_Class += '<p class="prereq_Text">'+prereqs+'</p>'
  describe_Class += '<p>'+"Units: "+class_Units+"; Term: "+class_Term+";  Grading: "+grading_Scheme+'</p>'
  describe_Class += '</div>'
  if (section_Info != {} || Object.keys(section_Info).length > 1) {describe_Class += '<div id="display_Sections"><button class="link_button" id="section_Button"></button></div>'}
  describe_Class += '</div>'
  describe_Class += '<div class="pt-1 class_Description_Text">'
  describe_Class += '<p>'+text_description+'</p>'
  describe_Class += '</div>'
  $('#class_Description').html(describe_Class);
  document.getElementById('add_Button_Click').onclick =
      function(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
        add_Class(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);}.bind(null, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);
  if (Object.keys(section_Info).length > 1) {
    let display_Section_Button = document.getElementById('section_Button')
    display_Section_Button.innerHTML = "(+)-Select Class Section";
    display_Section_Button.onclick =
        function(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
          display_Sections(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);}.bind(null, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);
        }

}

function round_Time(time) {
  // Extract the Hour and Minutes
  new_Time = time.split(":")
  hour = parseInt(new_Time[0],10)
  minutes = parseInt(new_Time[1],10)
  if (new_Time.length != 2) {
      console.log("Incorrect Input Time Format: ", time)
  }
  // Round Time to Nearest Half and Hour Interval
  if (minutes < 15) {
      minutes = "00";}
  else if (minutes < 45){
      minutes = "30";}
  else {
      minutes = "00";
      ++hour;}
  return String(hour) + ":" + String(minutes)
}

// Ask for User Section if One Availible
function display_Sections(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
    var section_Div = document.querySelector('#display_Sections');
    var display_Section_Button = document.querySelector('#section_Button');
    // Remove Section from Displa
    if (display_Section_Button.innerHTML === "(-)-Select Class Section") {
      sections_Removing = document.getElementsByClassName('sections');
      // Change Inner Text
      display_Section_Button.innerHTML = "(+)-Select Class Section";
      // Remove Sections from Display
      for (let i=sections_Removing.length-1; i >= 0; i--) {section_Div.removeChild(sections_Removing[i]);}
      return "Done";
    }
    display_Section_Button.innerHTML = "(-)-Select Class Section";
    let section_Info = section_Info_Holder[String(window.filter_Class_Term).toLowerCase()]
    for (var section_Key in section_Info) {
        // Create HTML to Hold Section Options
        let section_Holder = document.createElement('div')
        let users_Choice = document.createElement('input')
        let checkbox_Label = document.createElement('label')
        let section_Record = document.createElement('span')
        section_Holder.className = "sections"
        // Display Info of Section to User
        let section_Time = section_Info[section_Key]['section_Time']
        let section_Instructor = section_Info[section_Key]['section_Instructor']
        if (section_Time === "A") {section_Time = "TBA"}
        section_Record.innerText = "  Instructor: " + section_Instructor + "; Time: " + section_Time
        // Stylize Checkbox
        checkbox_Label.htmlFor = "radio"
        users_Choice.type = "radio"
        users_Choice.name ="find_Section"
        users_Choice.className = "myCheck"
        // Add Onlick to Checkbox to Add/Remove Class
        button_Classname_Identifier = "btn event_Button_Text event_Button event_Button_" + class_Code.replace(" ","_");
        var display_Button_Classname_Identifier = "btn button display_Class_Button";
        section_Number_Holder = parseInt(section_Key)
        users_Choice.onclick =
            function(button_Classname_Identifier, display_Button_Classname_Identifier, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder, section_Number_Holder) {
              switch_Section(button_Classname_Identifier, display_Button_Classname_Identifier, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder, section_Number_Holder);}.bind(null, button_Classname_Identifier, display_Button_Classname_Identifier, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder, section_Number_Holder);
        // Add the Option to the HTML
        section_Holder.appendChild(users_Choice)
        section_Holder.appendChild(checkbox_Label)
        section_Holder.appendChild(section_Record)
        section_Div.appendChild(section_Holder)
    }
}

function switch_Section(button_Classname_Identifier, display_Button_Classname_Identifier, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder, section_Number) {
  remove_Button([button_Classname_Identifier, display_Button_Classname_Identifier], class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);
  add_Class(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder, section_Number);
}

function edit_Total_Class_Conformations_Counter() {
  // Get All Classes to Recalculate Total Conformations
  var calendar_Events_List = document.querySelectorAll("#display_Added_Classes button");
  let previous_Total_Conformations = 1;
  let previous_Total_Conformations_Element = document.getElementById('total_Class_Conformation')
  previous_Total_Conformations_Element.innerText = previous_Total_Conformations
  for (var i = 0; i < calendar_Events_List.length; i++) {
      let calendar_Event = calendar_Events_List[i];
      let event_Listener_Info = calendar_Event.querySelector("p.hidden_Event_Listeners").innerText.split(",||| split the text here |||,");
      let section_Info_Holder = JSON.parse(event_Listener_Info[8]);
      let section_Info = section_Info_Holder[String(window.filter_Class_Term).toLowerCase()]
      console.log(section_Info_Holder, section_Info)

      // Find total Sections in Event that we are Losing/Gaining
      let num_Sections = 0;
      for (var section_Key in section_Info) {if (!["A", "+", "NA", "NaN"].includes(section_Info[section_Key]["section_Time"][0])) {num_Sections += 1}}
      if (num_Sections <= 1) {return false;}  // No Good New Sections Added (Either 0 or 1)
      //let previous_Total_Conformations = previous_Total_Conformations_Element.innerHTML
      previous_Total_Conformations = previous_Total_Conformations*num_Sections
      previous_Total_Conformations_Element.innerText = previous_Total_Conformations
  }
  // Save New Sections to Global window
  compile_Good_Sections_for_Conformation()
}

function change_Class_Conformation(mode) {
  // Find and Change Current Conformation number (Reset if at Final Stage)
  let current_Conformations_Element = document.getElementById('current_Class_Conformation')
  let previous_Total_Conformations_Element = document.getElementById('total_Class_Conformation')
  if (mode === "right") {current_Conformations_Element.innerHTML = parseInt(current_Conformations_Element.innerHTML) + 1}
  else if (mode === "left") {current_Conformations_Element.innerHTML = parseInt(current_Conformations_Element.innerHTML) - 1}
  if (parseInt(current_Conformations_Element.innerHTML) > parseInt(previous_Total_Conformations_Element.innerHTML)) {current_Conformations_Element.innerHTML = 1}
  if (parseInt(current_Conformations_Element.innerHTML) < 1) {current_Conformations_Element.innerHTML = 1}
  // Find all Good Sections in Current Class List
  if (parseInt(previous_Total_Conformations_Element.innerHTML) <= 1) {return false;}
  let steps_to_New_Conformation = window.good_Sections[parseInt(current_Conformations_Element.innerHTML) - 1]
  for (let i = 0; i < steps_to_New_Conformation.length; i ++) {
      let event_Listener_Info = steps_to_New_Conformation[i].split(",||| split the text here |||,");
      // Decompact Info into Variabls We Use
      let button_Classname_Identifier = event_Listener_Info[0]; let display_Button_Classname_Identifier = event_Listener_Info[1];
      let class_Code = event_Listener_Info[2]; let class_Term = event_Listener_Info[3]; let class_Units = event_Listener_Info[4];
      let class_Name = event_Listener_Info[5]; let prereqs = event_Listener_Info[6];
      let text_description = event_Listener_Info[7]; let section_Number = event_Listener_Info[9]
      let section_Info_Holder = JSON.parse(event_Listener_Info[8])
      let section_Info = section_Info_Holder[String(window.filter_Class_Term).toLowerCase()]
      // Switch One Section
      add_Description(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) // User Wont notice but an error wil fire if not present (else remove function changes add/remove button text of wrong class)
      switch_Section(button_Classname_Identifier, display_Button_Classname_Identifier, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder, section_Number)
  }
}

function compile_Good_Sections_for_Conformation() {
  // Find all Good Sections in Current Class List
  var calendar_Events_List = document.querySelectorAll("#display_Added_Classes button");
  var good_Sections = []
  for (var i = 0; i < calendar_Events_List.length; i++) {
    // Finall Class Information
    let calendar_Event = calendar_Events_List[i];
    let unsplit_Event_Listerner_Info = calendar_Event.querySelector("p.hidden_Event_Listeners").innerText
    let event_Listener_Info = unsplit_Event_Listerner_Info.split(",||| split the text here |||,");
    let section_Info_Holder = JSON.parse(event_Listener_Info[8]);
    let section_Info = section_Info_Holder[String(window.filter_Class_Term).toLowerCase()]
    // Get a List of all Possible Sections
    let current_Good_Sections = [];
    for (var section_Key in section_Info) {if (!["A", "+", "NA", "NaN"].includes(section_Info[section_Key]["section_Time"][0])) {current_Good_Sections.push(unsplit_Event_Listerner_Info + ",||| split the text here |||," + section_Key)}}
    good_Sections.push(current_Good_Sections)
  }
  let permuted_Good_Sections = [[]];
  permuted_Good_Sections = recursive_Permutation(good_Sections, permuted_Good_Sections)
  permuted_Good_Sections = permuted_Good_Sections.splice(0,permuted_Good_Sections.length-1) // Remove Last Element (Which is [] and leftover from recursion
  window.good_Sections = permuted_Good_Sections
}

// This Function will Permute the CLasses into a list of next steps. However, the LAST element will always be [] and should be deleted
function recursive_Permutation(good_Sections, permuted_Good_Sections) {
    // Base case
    if (good_Sections.length === 0) {
        permuted_Good_Sections.push([]);
        return permuted_Good_Sections;}
    // Recurse Down
    let good_Section = good_Sections[0]
    for (let i=0; i < good_Section.length; i++) {
        let good_Section_Value = good_Section[i];
        permuted_Good_Sections[permuted_Good_Sections.length - 1].push(good_Section_Value)
        permuted_Good_Sections = recursive_Permutation([...good_Sections].splice(1,good_Sections.length), permuted_Good_Sections)}
    return permuted_Good_Sections
}

function add_Activity() {
  // Get Info From Form
  let class_Term = window.filter_Class_Term;
  let class_Code = document.getElementById('added_Class_Name').value
  let class_Units = document.getElementById('added_Class_Units').value
  let text_description = document.getElementById('added_Class_Description').value
  let class_Times = document.getElementById('added_Class_Time').value
  let class_Loc = document.getElementById('added_Class_Loc').value
  let section_Info_Holder = {
      'first': {"01": {"section_Instructor": "NA", "section_Time": ["A"], "section_Loc": ["A"], "section_Grading": "NA"}},
      'second': {"01": {"section_Instructor": "NA", "section_Time": ["A"], "section_Loc": ["A"], "section_Grading": "NA"}},
      'third': {"01": {"section_Instructor": "NA", "section_Time": ["A"], "section_Loc": ["A"], "section_Grading": "NA"}}
  }
  section_Info_Holder[class_Term.toLowerCase()] = {"01": {"section_Instructor": "NA", "section_Time": class_Times.split(", "), "section_Loc": [class_Loc], "section_Grading": "NA"}}
  // Set Defaults if None given
  let class_Name = "Activity"
  let prereqs = "Prerequisites: NA"
  if (class_Times == "" || class_Times == " " || class_Times == undefined) {section_Info_Holder[class_Term.toLowerCase()] = {}}
  if (class_Name == "" || class_Name == " " || class_Name == undefined) {class_Name = "NA"}
  if (class_Units == "" || class_Units == " " || class_Units == undefined) {class_Units = "NA"}
  if (text_description == "" || text_description == " " || text_description == undefined) {text_description = "NA"}
  if (class_Code == "" || class_Code == " " || class_Code == undefined) {class_Code = "New"}
  // Close Form
  document.getElementById('close_Activity_Modal_Button').click()
  // Add Activity
  add_Description(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder)
  add_Class(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder)
}

// Function to Add Classes to the HTML Calendar Table
function add_Class(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder, section_Number = -1) {
  edit_Total_Units(class_Units, "add") // Add Total Units
  window.calendar_Add_on_Counter = window.calendar_Add_on_Counter + 1;

  // Get Section Info
  let section_Info = section_Info_Holder[String(window.filter_Class_Term).toLowerCase()]

  // Change Button Function to Remove Under the Class Details (Below Class Table)
  button_Classname_Identifier = "btn event_Button_Text event_Button event_Button_" + class_Code.replace(" ","_");
  var display_Button_Classname_Identifier = "btn button display_Class_Button";
  document.getElementById('add_Button_Click').onclick =
        function(button_Classname_Identifier, display_Button_Classname_Identifier, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
          remove_Button([button_Classname_Identifier, display_Button_Classname_Identifier], class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);}.bind(null, button_Classname_Identifier, display_Button_Classname_Identifier, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);
  document.querySelector('#add_Button_Click').innerText = 'Remove Class';

  // Place Button Under Class Display Section (Above Class Table)
  var display_button = document.createElement('button');
  display_button.onclick =
        function(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
          add_Description(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);}.bind(null, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);
  display_button.ondblclick =
        function(button_Classname_Identifier, display_Button_Classname_Identifier, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
          remove_Button([button_Classname_Identifier, display_Button_Classname_Identifier], class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);}.bind(null, button_Classname_Identifier, display_Button_Classname_Identifier, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);
  display_button.onmousedown =
        function(button_Classname_Identifier, display_Button_Classname_Identifier, class_Code) {
          change_Btn_Colors([button_Classname_Identifier, display_Button_Classname_Identifier], class_Code)}.bind(null, button_Classname_Identifier, display_Button_Classname_Identifier, class_Code);
  display_button.onmouseup = function() {window.color_Changing_Time = false;}
  display_button.onmouseout = function() {window.color_Changing_Time = false;}
  display_button.className = display_Button_Classname_Identifier;
  display_button.innerText = class_Code;
  display_button.style.backgroundColor = window.calendar_Event_Colors[window.calendar_Add_on_Counter%window.calendar_Event_Colors.length];
  btn_Hidden = document.createElement('p')
  btn_Hidden.className = 'hidden_Event_Listeners'
  btn_Hidden.innerText = [button_Classname_Identifier, "||| split the text here |||", display_Button_Classname_Identifier, "||| split the text here |||", class_Code, "||| split the text here |||", class_Term, "||| split the text here |||", class_Units, "||| split the text here |||", class_Name, "||| split the text here |||", prereqs, "||| split the text here |||", text_description, "||| split the text here |||", JSON.stringify(section_Info_Holder)]
  display_button.appendChild(btn_Hidden).html;
  btn_Hidden.hidden = true
  var class_List_Display = document.querySelector('#display_Added_Classes');
  class_List_Display.appendChild(display_button).html;
  savePageState();

  // Get Info from section_Info
  if (Object.keys(section_Info).length === 0) {console.log("No Times Listed for the Class :("); return false;}
  var {start_Time_List, end_Time_List, class_Days_List} = get_Time_Info_From_Section(section_Info, section_Number)
  var class_Location_List = get_Loc_Info_From_Section(section_Info, section_Number)
  // Add ALL Times in ONE Section
  for (var section_Part = 0; section_Part < start_Time_List.length; section_Part++) {
      var class_Location = class_Location_List[section_Part]
      var start_Time = start_Time_List[section_Part]
      var class_Days = class_Days_List[section_Part]
      var end_Time = end_Time_List[section_Part]
      // Round the Time to a Half an Hour
      if (start_Time === "NA" && end_Time === "NA") {start_Time="0:00";end_Time="0:00"}
          start_Time = round_Time(start_Time)
          end_Time = round_Time(end_Time)
      // Dont Add to Calender Table if No Times
      if (start_Time === "0:00" && end_Time === "0:00") {return "Ending Script Here"}
      // Add Event to Calendar
      for (var day_Index=0; day_Index < class_Days.length; day_Index++) {
          day = class_Days[day_Index]
          // Find Start and End ID
          var start_ID = day + "-" + start_Time;
          var end_ID = day + "-" + end_Time;
          // Loop Until You Reach End Time
          var mid_Time = start_Time;
          var mid_ID = start_ID;
          var btn, calendar_Cell;
          // Loop From Start to End Time
          num_Added = 1;
          inner_loop:
          while (true) {
              // Increase Time (mid_Time) Until You Find the Final End Time
              var mid_Minute = parseInt(mid_Time.split(":")[1],10);
              var mid_Hour = parseInt(mid_Time.split(":")[0],10);
              if (mid_Minute === 0) {
                mid_ID = day + "-" + String(mid_Hour) + ":30";}
              else {
                mid_ID = day + "-" + String(mid_Hour+1) + ":00";}
              mid_Time = mid_ID.split("-")[1];
              if (mid_ID === end_ID) {break inner_loop;}
              // Note the Number of 30 min Time Periods Passed (Each are 1.5rem in height)
              num_Added++
            }
          // Make One Button/day, adding class and onclick event
          btn = document.createElement('button');
          btn.className = button_Classname_Identifier;
          btn.onclick =
                function(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
                  add_Description(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);}.bind(null, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);
          btn.ondblclick =
                function(button_Classname_Identifier, display_Button_Classname_Identifier, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
                  remove_Button([button_Classname_Identifier, display_Button_Classname_Identifier], class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);}.bind(null, button_Classname_Identifier, display_Button_Classname_Identifier, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);
          // Get Parent on Table (The Start Time) To Place the Button
          console.log(day)
          calendar_Cell = document.querySelector('#' + day);
          // Customize Button Height/Width to Match CURRENT Table (zooming is messing things up now)
          btn.style.height = String(1.5*num_Added) + "rem";
          btn.style.width = "100%"
          btn.style.marginLeft = "0%"
          let from_Top = get_Distance_From_Top(start_Time);
          btn.style.top = String(from_Top) + "rem";
          // Add Button color
          btn.style.backgroundColor = window.calendar_Event_Colors[window.calendar_Add_on_Counter%window.calendar_Event_Colors.length];
          // Add Text to button
          btn_Time = document.createElement('p');
          btn_Time.className = "reduce_Event_Button_Text"
          btn_Time.innerText = to_Clock_Time(start_Time) + " - " + to_Clock_Time(end_Time);
          btn_Class = document.createElement('p');
          btn_Class.innerText = class_Code;
          btn_Loc = document.createElement('p');
          btn_Loc.className = "reduce_Event_Button_Text"
          btn_Loc.innerText = class_Location
          btn_Hidden = document.createElement('p')
          btn_Hidden.className = 'hidden_Event_Listeners'
          btn_Hidden.innerText = [button_Classname_Identifier, "||| split the text here |||", display_Button_Classname_Identifier, "||| split the text here |||", class_Code, "||| split the text here |||", class_Term, "||| split the text here |||", class_Units, "||| split the text here |||", class_Name, "||| split the text here |||", prereqs, "||| split the text here |||", text_description, "||| split the text here |||", JSON.stringify(section_Info_Holder)]
          btn_Div = document.createElement('div');
          btn_Div.appendChild(btn_Time).html; btn_Div.appendChild(btn_Class).html; btn_Div.appendChild(btn_Loc).html; btn_Div.appendChild(btn_Hidden).html;
          btn.appendChild(btn_Div)
          btn_Hidden.hidden = true;
          // Resize Elements to Fit in Column
          fix_Overlapping_Events(calendar_Cell, btn, "add");
          // Finally, Add the New Event
          calendar_Cell.appendChild(btn).html;
      }
    }
    edit_Total_Class_Conformations_Counter()
    savePageState();
}


function remove_Button(event_Class_ID_List, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
  // Change Button Click Text/OnClick to Add class
  var remove_Class = document.getElementById('add_Button_Click').onclick =
      function(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
        add_Class(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);}.bind(null, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);
  document.querySelector('#add_Button_Click').innerText = 'Add Class';
  // Removes an element from the document
  var events = document.getElementsByClassName(event_Class_ID_List[0]);
  while (events[0]) {
    fix_Overlapping_Events(events[0].parentNode, events[0], "remove");
    events[0].parentNode.removeChild(events[0]);}
  // Remove Button in the Display Class List Section
  var display_Button = document.getElementsByClassName(event_Class_ID_List[1]);
  var display_Button_Copy = [...display_Button];
  for (var i=display_Button.length-1; i >= 0; i--) {
    if (display_Button[i].innerText === class_Code) {
      edit_Total_Units(class_Units, "remove")
      fix_Overlapping_Events(display_Button[0].parentNode, display_Button[i], "remove");
      display_Button[0].parentNode.removeChild(display_Button[i]);}}
  edit_Total_Class_Conformations_Counter()
  savePageState();
}

function to_Clock_Time(time) {
  // Extract the Hour and Minutes
  new_Time = time.split(":");
  hour = parseInt(new_Time[0],10);
  minutes = parseInt(new_Time[1],10);
  // If Hour is more than 12, subtract 12
  if (hour > 12 && hour < 24) {
    hour = hour - 12;}
  else if (hour === 24) {
    hour = 0;}
  // Get Minutes to 2 Decimals
  if (minutes === 0) {
      minutes = "00";}
  return String(hour) + ":" + String(minutes)
}

function get_Distance_From_Top(time) {
  // Extract the Hour and Minutes
  var new_Time = time.split(":");
  var hour = parseInt(new_Time[0],10);
  var minutes = parseInt(new_Time[1],10);
  // Find Hour Gap
  var time_Gap = hour - 8;
  // Add on the Minute Gap
  if (minutes === 30) {
    time_Gap = time_Gap + 0.5;}
  else if (minutes === 0) {
    time_Gap = time_Gap;}
  else {
    console.log("Cant Find Distant From Top. The Minutes isnt 0 or 30")}
  // Convert time to distance
  var distance_From_Top = String(time_Gap*3) // in rem (It Starts in Middle)
  return distance_From_Top
}

function change_Term(new_Term) {
  window.filter_Class_Term = new_Term;
  load_TermState() // Display Saved State for New Term
  find_Classes() // Display Class Table
}

function edit_Total_Units(class_Units, stage) {
  if (class_Units[0] === "+" || class_Units[0] === "" || class_Units[0] === " ") {class_Total_Units = "NA";}
  else {class_Total_Units = class_Units.split("-").reduce(function(a, b) {return parseFloat(a) + parseFloat(b);}, 0);}
  if (isNaN(class_Total_Units)) {class_Total_Units = "NA";}
  else {class_Total_Units = parseInt(class_Total_Units)}
  // If Units are Not There
  if (Number.isInteger(class_Total_Units) === false) {return "No New Units to Edit"}
  // Find Total Units for the Class (To Remove Later Below)
  var total_Units = document.getElementById('units');
  if (stage === "remove") {total_Units.innerText = parseInt(total_Units.innerText) - class_Total_Units}
  else if (stage === "add") {total_Units.innerText = parseInt(total_Units.innerText) + class_Total_Units}
  else {console.log("Not Sure if We are Adding or Removing Units")}
  // Decide Whether or not to Dispay unit section
  display_Units()
}

function display_Units() {
  var unit_Section = $('#cumulative_Class_Info')
  var total_Units = parseInt( $('#units').html());
  if(total_Units > 0) {unit_Section.show();}
  else {unit_Section.hide();}
}

function find_Classes() {
  console.log(window.filter_Class_Term)
  class_Table_Body = document.getElementById("class_Data")
  class_Table_Body.querySelectorAll('*').forEach(n => n.remove());
  $.getJSON("Database/department_data_Old_Style.json", {}, function(json) {
    var data = eval(json); // this will convert your json string to a javascript object
    for (var key in data) {
        // this will check if key is owned by data object and not by any of it's ancestors
        if (data.hasOwnProperty(key)) {
          // Get Class Data From Row
          let class_Code = data[key]['class_Code']                // Class Code: CS 1
          let class_Term = data[key]['class_Term']                // Class Term: First Term
          let class_Units = data[key]['class_Units']              // Class Name: Introduction to Computer Programming
          let class_Name = data[key]['class_Name']                // Class Name: Introduction to Computer Programming
          let prereqs = data[key]['class_Prereqs']                // Example: Prerequisites: CS 1 or equivalent
          let text_description = data[key]['class_Description']   // Description of Class
          let section_Info_Holder = data[key]['section_Info']
          // Place Holders for Variables
          if (prereqs === "NA" || prereqs === "" || prereqs === " ") {prereqs = "Prerequisites: NA";}
          if (class_Term === "NA" || class_Term === "" || class_Term === " ") {class_Term = "NA";}
          if (text_description === "NA" || text_description === "" || text_description === " ") {text_description = "Description: NA";}
          // Only Place in Table if in Correct Term
          if (class_Term.toUpperCase().includes(window.filter_Class_Term.toUpperCase()) === false && class_Term != "NA") {continue;}
          // Find the Total Class Units (if Given).
          if (class_Units === "+" || class_Units === "" || class_Units === " ") {class_Total_Units = "NA";}
          else {class_Total_Units = class_Units.split("-").reduce(function(a, b) {return parseFloat(a) + parseFloat(b);}, 0);}
          if (isNaN(class_Total_Units)) {class_Total_Units = "NA";}
          else {class_Total_Units = parseInt(class_Total_Units)}
          // Populate Display Table in HML (ON CLICK of the Class Code show Description)
          class_Table_Body = document.getElementById("class_Data")
          let class_Row = class_Table_Body.insertRow(0);
          let code_Cell = class_Row.insertCell(0); let unit_Cell = class_Row.insertCell(1); let name_Cell = class_Row.insertCell(2);
          let code_Button = document.createElement('button');
          code_Button.innerHTML = class_Code; code_Button.className = 'link_button'; code_Button.id = class_Code;
          code_Cell.appendChild(code_Button);
          unit_Cell.innerHTML = class_Total_Units;
          name_Cell.innerHTML = class_Name;
          class_Table_Body.appendChild(class_Row);
          // Add the Onlick Events to the Class Code link
          code_Button.onclick =
                function(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
                  add_Description(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);}.bind(null, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);
          code_Button.ondblclick =
                function(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
                  add_Class(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);}.bind(null, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);
        }
    }
  })
}

function add_Onclick_Events_Back(events, color_Control = false) {
  for (var i = 0; i < events.length; i++) {
    let calendar_Event = events[i];
    let event_Listener_Info = calendar_Event.querySelector("p.hidden_Event_Listeners").innerText.split(",||| split the text here |||,");
    let button_Classname_Identifier = event_Listener_Info[0]; let display_Button_Classname_Identifier = event_Listener_Info[1];
    let class_Code = event_Listener_Info[2]; let class_Term = event_Listener_Info[3]; let class_Units = event_Listener_Info[4];
    let class_Name = event_Listener_Info[5]; let prereqs = event_Listener_Info[6];
    let text_description = event_Listener_Info[7];
    let section_Info_Holder = JSON.parse(event_Listener_Info[8]);
    calendar_Event.onclick =
          function(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
            add_Description(class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);}.bind(null, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);
    calendar_Event.ondblclick =
          function(button_Classname_Identifier, display_Button_Classname_Identifier, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder) {
            remove_Button([button_Classname_Identifier, display_Button_Classname_Identifier], class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);}.bind(null, button_Classname_Identifier, display_Button_Classname_Identifier, class_Code, class_Term, class_Units, class_Name, prereqs, text_description, section_Info_Holder);
    if (color_Control) {
        calendar_Event.onmousedown =
              function(button_Classname_Identifier, display_Button_Classname_Identifier, class_Code) {
                change_Btn_Colors([button_Classname_Identifier, display_Button_Classname_Identifier], class_Code)}.bind(null, button_Classname_Identifier, display_Button_Classname_Identifier, class_Code);
        calendar_Event.onmouseup = function() {window.color_Changing_Time = false;}
        calendar_Event.onmouseout = function() {window.color_Changing_Time = false;}
    }
  }

}

function load_TermState() {
  // Load variables
  let term_PageState;
  let current_Term = window.filter_Class_Term
  let current_Class_List = document.getElementById("display_Added_Classes");
  let current_Class_Units = document.getElementById("cumulative_Class_Info");
  let current_Calendar_State = document.getElementById("calendar_Body");
  // Get State for the Specific Term we are in
  if (current_Term === "First") {term_PageState = window.pageState.First}
  else if (current_Term === "Second") {term_PageState = window.pageState.Second}
  else if (current_Term === "Third") {term_PageState = window.pageState.Third}
  // Get Data From Term
  let previous_Class_List = term_PageState.class_List;
  let previous_Class_Units = term_PageState.class_Units;
  let previous_Calendar_State = term_PageState.calendar_State;
  // Add Previous State to HTML Elements
  current_Class_List.innerHTML = previous_Class_List //current_Class_List.parentNode.replaceChild(previous_Class_List, current_Class_List);
  current_Class_Units.innerHTML = previous_Class_Units;
  current_Calendar_State.innerHTML = previous_Calendar_State //parentNode.replaceChild(previous_Calendar_State, current_Calendar_State);
  // Get Onclick Events backgroundColor
  var calendar_Events = document.querySelectorAll("#calendar_Body button");
  var calendar_Events_List = document.querySelectorAll("#display_Added_Classes button");
  add_Onclick_Events_Back(calendar_Events, false)
  add_Onclick_Events_Back(calendar_Events_List, true)
  // Show Units/Conformations in New State
  edit_Total_Class_Conformations_Counter()
  display_Units()
}

function savePageState() {
  // Get Page Info for a Given term
  let term_PageState;
  let current_Term = window.filter_Class_Term;
  if (current_Term === "First") {term_PageState = window.pageState.First}
  else if (current_Term === "Second") {term_PageState = window.pageState.Second}
  else if (current_Term === "Third") {term_PageState = window.pageState.Third}
  // Store the Term Info
  term_PageState.class_List = document.getElementById("display_Added_Classes").innerHTML
  term_PageState.class_Units = document.getElementById("cumulative_Class_Info").innerHTML
  term_PageState.calendar_State = document.getElementById("calendar_Body").innerHTML
  // Save the Term Info
  localStorage.setItem('pageState', JSON.stringify(window.pageState));
}

// Get Data into Tabular Form When Searching
$(document).ready(function(){
  // Initialize the Homepage
  if (typeof window.filter_Class_Term === 'undefined') {window.filter_Class_Term = "First"} // Display Only First Term
  // Check if Previous State is Availilbe
  window.pageState = JSON.parse(localStorage.getItem('pageState'));
  // Change this number if you want to clear all stored cookies/cache after a major change to the database
  let refresh_Update_Number = 0
  if (window.pageState === null || window.pageState.Updated != refresh_Update_Number) {
    let current_Class_List = document.getElementById("display_Added_Classes");
    let current_Calendar_State = document.getElementById("calendar_Body");
    let current_Class_Units = document.getElementById("cumulative_Class_Info");
    // Create a Local Storage for the New State
    window.pageState = {
      First: {
        class_List: current_Class_List.innerHTML,
        class_Units: current_Class_Units.innerHTML,
        calendar_State: current_Calendar_State.innerHTML},
      Second: {
        class_List: current_Class_List.innerHTML,
        class_Units: current_Class_Units.innerHTML,
        calendar_State: current_Calendar_State.innerHTML},
      Third: {
        class_List: current_Class_List.innerHTML,
        class_Units: current_Class_Units.innerHTML,
        calendar_State: current_Calendar_State.innerHTML},
      Updated: refresh_Update_Number
    };
    savePageState();}
  else {
    // Retrieve Previous State
    console.log("Found Previous Page State")
    load_TermState()
  }
  // Display Classes and Units
  display_Units()  // Display Units if > 0
  find_Classes() // Display Class Table
});
