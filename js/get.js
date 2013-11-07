function prefix(str) {
	// Split up the JSON formatted data
	var data = str.split("END");

	// Add a new table to the prefix section of the page
	var table = $('<table></table>').addClass('table');
        var thead = $('<thead></thead>');
        var theadRow = $('<tr></tr>');

        thead.append(theadRow);
        table.append(thead);
	
	// Create the table headers 
	var headers = ["Router", "Timestamp", "Prefix", "Status"];
	for (var i in headers) {
		var row = $('<td></td>').text(headers[i]);
		theadRow.append(row);
	}

	// Create the body of the table
	var tbody = $('<tbody></tbody>');
	table.append(tbody);

	// Cycle through the data
	for (var i in data) {
		// Parse the JSON
		var obj = jQuery.parseJSON(data[i]);
		var row = $('<tr></tr>');
		var tmp;

		// Add the router
		tmp = $('<td rowspan="' + obj.prefixes.length + '"></td>');
		tmp.text(obj.router);
		row.append(tmp);

		// Cycle through the routers advertised prefixes
		for (var k in obj.prefixes) {
			// Add the timestamp - run through the validTimestamp function to
			// see if the timestamp has expired
			tmp = $('<td></td>');
			if (obj.prefixes[k].timestamp === "-") {
				tmp.text("-");
			} else {
				tmp.text(new Date(obj.prefixes[k].timestamp * 1000));
			}
			row.append(tmp);

			// Add the prefix
			tmp = $('<td></td>');
			tmp.text(obj.prefixes[k].prefix);
			row.append(tmp);

			var modifier;

			if (obj.prefixes[k].timestamp !== "-" && obj.prefixes[k].status !== "Offline" && !validTimestamp(obj.prefixes[k].timestamp)) {
				modifier = "warning";
				obj.prefixes[k].status = "Out-of-Date";
                        } else if (obj.prefixes[k].status === "Online") {
                                modifier = "success";
                        } else if (obj.prefixes[k].status === "Offline") {
                                modifier = "danger";
                        } else {
                                modifier = "unavailable";
				obj.prefixes[k].status = "NPT";
                        }
	
			// Add the status
			tmp = $('<td></td>').addClass(modifier + ' text-center');
			tmp.text(obj.prefixes[k].status);
			row.append(tmp);
	
			// Append the data to the table and move to the next row
			tbody.append(row);
			row = $('<tr></tr>');
		}
	}

	// Add the table to the page
        $('#advertisedPrefixes').append(table);
}

function link(str) {
	// Split up the JSON formatted data
        var data = str.split("END");

        // Add a new table to the prefix section of the page
        var table = $('<table></table>').addClass('table');
        var thead = $('<thead></thead>');
        var theadRow = $('<tr></tr>');

        thead.append(theadRow);
        table.append(thead);

        // Create the table headers 
        var headers = ["Router", "LSA Timestamp", "Links", "Status"];
        for (var i in headers) {
                var row = $('<td></td>').text(headers[i]);
                theadRow.append(row);
        }

        // Create the body of the table
        var tbody = $('<tbody></tbody>');
        table.append(tbody);

        // Cycle through the data
        for (var i in data) {
                // Parse the JSON
                var obj = jQuery.parseJSON(data[i]);
                var row = $('<tr></tr>');
                var tmp;

                // Add the router
                tmp = $('<td rowspan="' + obj.links.length + '"></td>');
                tmp.text(obj.router);
		console.log("Node: " + obj.router)
                row.append(tmp);

		// Add the timestamp - process via the validTimestamp func
		tmp = $('<td rowspan="' + obj.links.length + '"></td>');
		
		if (obj.timestamp === "-") {
			tmp.text("-");
		} else {
			tmp.text(new Date(obj.timestamp * 1000));
		}
		row.append(tmp);

                // Cycle through the routers links
                for (var k in obj.links) {
                        // Add the prefix
                        tmp = $('<td></td>').text(obj.links[k].link);
                        row.append(tmp);
			console.log("\tLink: " + obj.links[k].link)

			var modifier;
	
			if (obj.timestamp !== "-" && obj.links[k].status !== "Offline" && !validTimestamp(obj.timestamp)) {
				modifier = "warning";
				obj.links[k].status = "Out-of-Date";
                        } else if (obj.links[k].status === "Online") {
                                modifier = "success";
                        } else if (obj.links[k].status === "Offline") {
                                modifier = "danger";
                        } else {
                                modifier = "unavailable";
				obj.links[k].status = "NPT";
                        }

                        // Add the status
                        tmp = $('<td></td>').addClass(modifier + ' text-center');
			tmp.text(obj.links[k].status);
                        row.append(tmp);

                        // Append the data to the table and move to the next row
                        tbody.append(row);
                        row = $('<tr></tr>');
                }
        }

	// Add the table to the page
	$('#linkStatus').append(table);
}

function validTimestamp(time) {
	var curTime = new Date().getTime();
	time = time * 1000;
	var diff = curTime - time;

	console.log(curTime + " : " + time + " : " + diff);

	if (diff < 2400000) {
		return true;
	} else {
		return false;
	}
}
