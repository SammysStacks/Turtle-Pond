
function check_Degree(department) {
  // Get Page Info for a Given term
  let term_PageState = [window.pageState.First.class_List, window.pageState.Second.class_List, window.pageState.Third.class_List]
  annual_Class_List = []
  // Loop through each Term to get Class Info
  for (let i = 0; i < term_PageState.length; i++) {
    // Get Class List for Respective Term
    let term_Classes = term_PageState[i];

    let node_BluePrint = document.getElementById("display_Added_Classes");
    var range = document.createRange();
    range.selectNodeContents(node_BluePrint);
    term_Classes = range.createContextualFragment(term_Classes);
    console.log(term_Classes)
    console.log(term_Classes.innerHTML)


    for (let j = 0; j < class_List_Holder.length; j++) {
      let class_Code = class_List_Holder[j].innerHTML
      console.log(class_Code)
      annual_Class_List.push(class_Code)
    }
    console.log(annual_Class_List)
  }
}
