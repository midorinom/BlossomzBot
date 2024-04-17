function onChange(e) {
    // Run this script only for the Holding Area sheet
    if (SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getName() !== "Holding Area") {
      return;
    }
    
    const holdingAreaSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Holding Area");
    let holdingAreaData = holdingAreaSheet.getDataRange().getValues();
    const discordUrl = "https://discord.com/api/webhooks/1230173537063403540/Y9udtgvGj8mDQ-0CAueR0QDdbZKiXyMvtS3Twwc28tICTsF8PKkPvjl-R-R3i38CPavW"; // Blossomz
    // const discordUrl = "https://discord.com/api/webhooks/1230151929934385254/3HkSB0L4pyNmOOYh0SnZGP3H6DjaoIssS2moe4C0upXZpzaASH-dV8XgCxK1Vs1GsPkq"; // Dev Server
    var discordMessage = "";
  
    // Column Numbers
    const holdingAreaPrevRoleColumn = 0;
    const holdingAreaNewRoleColumn = 1;
    const holdingAreaDisplayNameColumn = 2;
    const holdingAreaDiscordUsernameColumn = 3;
    const holdingAreaDateJoinedColumn = 4;
    const holdingAreaMemberIdColumn = 5;
  
    if (holdingAreaData.length > 1) {
        // Looping through the rows of Holding Area
        for (let i = 2; i < holdingAreaData.length; i++) {
          const currentRowHoldingArea = holdingAreaData[i];
          const prevRole = currentRowHoldingArea[holdingAreaPrevRoleColumn];
          const newRole = currentRowHoldingArea[holdingAreaNewRoleColumn];
  
          // There is a New Role
          if (newRole) {
            const sheetToUpdate = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(newRole);
            let dataSheetToUpdate = sheetToUpdate.getDataRange().getValues();
            let sheetToUpdateDisplayNameColumn = 0;
            let sheetToUpdateDiscordUsernameColumn = 0;
            let sheetToUpdateDateJoinedColumn = 0;
            let sheetToUpdateRemarksColumn = 0;
            let sheetToUpdateMemberIDColumn = 0;
  
            // Get all Columns of the Sheet that is to be Updated, by looping through the first row (Heading)
            for (let j = 0; j < dataSheetToUpdate[0].length; j++) {
              if (dataSheetToUpdate[0][j] === "Display Name") {
                sheetToUpdateDisplayNameColumn = j;
              }
              if (dataSheetToUpdate[0][j] === "Discord Username") {
                sheetToUpdateDiscordUsernameColumn = j;
              }
              if (dataSheetToUpdate[0][j] === "Date Joined") {
                sheetToUpdateDateJoinedColumn = j;
              }
              if (dataSheetToUpdate[0][j] === "Remarks") {
                sheetToUpdateRemarksColumn = j;
              }
              if (dataSheetToUpdate[0][j] === "Member ID") {
                sheetToUpdateMemberIDColumn = j;
              }
            } 
  
            // Check if member already exists. Update if yes, otherwise append a new row
            let memberExists = false;
  
            for (let j = 1; j < dataSheetToUpdate.length; j++) {
              if (dataSheetToUpdate[j][sheetToUpdateMemberIDColumn] === currentRowHoldingArea[holdingAreaMemberIdColumn]) {
                const newData = [...dataSheetToUpdate[j]];
                newData[sheetToUpdateDisplayNameColumn] = currentRowHoldingArea[holdingAreaDisplayNameColumn];
                newData[sheetToUpdateDiscordUsernameColumn] = currentRowHoldingArea[holdingAreaDiscordUsernameColumn];
                newData[sheetToUpdateDateJoinedColumn] = currentRowHoldingArea[holdingAreaDateJoinedColumn];
  
                const rangeSheetToUpdate = sheetToUpdate.getRange(j + 1, 1, 1, dataSheetToUpdate[j].length);
                rangeSheetToUpdate.setValues([newData]);
                
                discordMessage = currentRowHoldingArea[holdingAreaDisplayNameColumn] + " (" + currentRowHoldingArea[holdingAreaDiscordUsernameColumn] + ") " + "has been updated in the " + currentRowHoldingArea[holdingAreaNewRoleColumn] + " sheet.";
                const payload = JSON.stringify({content: discordMessage});
                const params = {
                  method: "POST",
                  payload: payload,
                  muteHttpExceptions: true,
                  contentType: "application/json"
                };
                const response = UrlFetchApp.fetch(discordUrl, params);
  
                memberExists = true;
                break;
              }
            }
  
            if (!memberExists) {
              const newData = Array(dataSheetToUpdate[0].length).fill("");
  
              // If there is a previous role, store the Remarks data from the previous spreadsheet first
              if (prevRole) {
                const prevSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(prevRole);
                let dataPrevSheet = prevSheet.getDataRange().getValues();
                let prevSheetMemberIDColumn = 0;
                let prevSheetRemarksColumn = 0;
  
                // Get Member ID Column
                for (let j = 0; j < dataPrevSheet[0].length; j++) {
                  if (dataPrevSheet[0][j] === "Member ID") {
                    prevSheetMemberIDColumn = j;
                  }
                  if (dataPrevSheet[0][j] === "Remarks") {
                    prevSheetRemarksColumn = j;
                  }
                } 
  
                // Find the row that has the Member ID, then store the remarks
                for (let j = 1; j < dataPrevSheet.length; j++) {
                  if (dataPrevSheet[j][prevSheetMemberIDColumn] === currentRowHoldingArea[holdingAreaMemberIdColumn]) {
                    newData[sheetToUpdateRemarksColumn] = dataPrevSheet[j][prevSheetRemarksColumn];
                  }
                }
              }
  
              newData[sheetToUpdateDisplayNameColumn] = currentRowHoldingArea[holdingAreaDisplayNameColumn];
              newData[sheetToUpdateDiscordUsernameColumn] = currentRowHoldingArea[holdingAreaDiscordUsernameColumn];
              newData[sheetToUpdateDateJoinedColumn] = currentRowHoldingArea[holdingAreaDateJoinedColumn];
              newData[sheetToUpdateMemberIDColumn] = currentRowHoldingArea[holdingAreaMemberIdColumn];
  
              sheetToUpdate.appendRow(newData);
  
              discordMessage = currentRowHoldingArea[holdingAreaDisplayNameColumn] + " (" + currentRowHoldingArea[holdingAreaDiscordUsernameColumn] + ") " + "has been added to the " + currentRowHoldingArea[holdingAreaNewRoleColumn] + " sheet.";
              const payload = JSON.stringify({content: discordMessage});
              const params = {
                method: "POST",
                payload: payload,
                muteHttpExceptions: true,
                contentType: "application/json"
              };
              const response = UrlFetchApp.fetch(discordUrl, params);
            }
  
            // Delete the Holding Area Row
            holdingAreaSheet.deleteRow(i + 1);
          }
  
          // There is a Previous Role
          if (prevRole && prevRole !== newRole) {
            const sheetToUpdate = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(prevRole);
            let dataSheetToUpdate = sheetToUpdate.getDataRange().getValues();
            let sheetToUpdateMemberIDColumn = 0;
  
            // Get Member ID Column
            for (let j = 0; j < dataSheetToUpdate[0].length; j++) {
              if (dataSheetToUpdate[0][j] === "Member ID") {
                sheetToUpdateMemberIDColumn = j;
              }
            } 
  
            // Find the row that has the Member ID, then delete it
            for (let j = 1; j < dataSheetToUpdate.length; j++) {
              if (dataSheetToUpdate[j][sheetToUpdateMemberIDColumn] === currentRowHoldingArea[holdingAreaMemberIdColumn]) {
                sheetToUpdate.deleteRow(j + 1);
  
                discordMessage = currentRowHoldingArea[holdingAreaDisplayNameColumn] + " (" + currentRowHoldingArea[holdingAreaDiscordUsernameColumn] + ") " + "has been deleted from the " + currentRowHoldingArea[holdingAreaPrevRoleColumn] + " sheet.";
                const payload = JSON.stringify({content: discordMessage});
                const params = {
                  method: "POST",
                  payload: payload,
                  muteHttpExceptions: true,
                  contentType: "application/json"
                };
                const response = UrlFetchApp.fetch(discordUrl, params);
              }
            }
  
            // Delete the Holding Area Row
            holdingAreaSheet.deleteRow(i + 1);
          }
      }
    }
  }