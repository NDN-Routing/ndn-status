	/*
	Script used to retrieve status content based on the given names, and update the tables
	on the status page
	
	Adam Alyyan - aalyyan@memphis.edu
*/

hostip = "141.225.11.173";
pubprefix = "/ndn/memphis.edu/status";
var ndn;
var face;

console.log("In: " + pubprefix);

// Enables the tabs to work
$('#myTab a').click(function (e) {
	e.preventDefault()
	$(this).tab('show')
})

var AsyncGetClosure = function AsyncGetClosure() {
	Closure.call(this);
};

function onData(interest, data) {
	console.log("Got data");
	console.log(data)
               //var content = upcallInfo.contentObject;
		console.log("Name: " + data.name.getName())
                var nameStr = data.name.getName().split("/").slice(4,5);
		console.log(nameStr)

                if (nameStr == "prefix") {
                        // Grab the JSON content and parse via the prefix function
                        var s = DataUtils.toString(data.content);
			console.log("S IS: " + s);
                        prefix(s);
                } else if (nameStr == "link") {
                        // Grab the JSON content and parse via the link function
                        var s = DataUtils.toString(data.content);
                        link(s);
                } else {
                        // Grab the JSON content and update the status information section
                        var data = DataUtils.toString(data.content);
                        var obj = jQuery.parseJSON(data);

                        document.getElementById("lastupdated").innerHTML = obj.lastupdated;
                        document.getElementById("lastlog").innerHTML = obj.lastlog;
                        document.getElementById("lasttimestamp").innerHTML = obj.lasttimestamp;
                }
}

AsyncGetClosure.prototype.upcall = function(kind, upcallInfo, tmp) {
	if (kind == Closure.UPCALL_FINAL) {
		console.log("oops...\n");
		// Do nothing.
	} else if (kind == Closure.UPCALL_CONTENT) {
		console.log("Got data");
		var content = upcallInfo.contentObject;
		var nameStr = content.name.getName().split("/").slice(5,6);

		if (nameStr == "prefix") {
			// Grab the JSON content and parse via the prefix function
			var s = DataUtils.toString(content.content);
			prefix(s);
		} else if (nameStr == "link") {
			// Grab the JSON content and parse via the link function
			var s = DataUtils.toString(content.content);
			link(s);
		} else {
			// Grab the JSON content and update the status information section
			var data = DataUtils.toString(content.content);
			var obj = jQuery.parseJSON(data);
			
			document.getElementById("lastupdated").innerHTML = obj.lastupdated;
			document.getElementById("lastlog").innerHTML = obj.lastlog;
			document.getElementById("lasttimestamp").innerHTML = obj.lasttimestamp;
		}
	} else if (kind == Closure.UPCALL_INTEREST_TIMED_OUT) {
		// Display an error in the update area

		// Log action to the console
		console.log("Closure.upcall called with interest time out.");
	}

	return Closure.RESULT_OK;
};

function getStatus(name) {
	console.log("loading...");

	// Passing a temporary interest object
	var interest = new Interest("/tmp/");
	
	// Specify that we want the latest content
	interest.childSelector = 1;
	interest.interestLifetime = 4000;

	// Retrieve the interest using the status name with a specifier appended to the end
	// to specify what content we want
	face.expressInterest(new Name(pubprefix + "/" + name), interest, onData, null);
	//face.expressInterest(new Name(pubprefix + "/" + name), new AsyncGetClosure());
}

$(document).ready(function() {
	var ospfnRunning;

	$.ajax({ url: 'scripts/ospfnCheck.php',
		 type: 'get',
		 success: function(output) {
			
			output = output.replace(/\s/gm, '');

			if (output === "Down") {
				ospfnRunning = false;
			} else {
				ospfnRunning = true;
			}
		 }
	});

	$.get("scripts/execute.php", function() {
		openHandle = function() {
			console.log("Connected");
			getStatus("metadata");
			getStatus("prefix");
			getStatus("link");
		};

		closeHandle = function() {
			 $('.alert-message')
                         	.append('<div class="alert alert-danger">NDN.js could not establish a connection to Netlogic. Please check back soon.</div>')
                                .fadeIn(500);
		};

		//ndn = new NDN({host:hostip, onopen:openHandle, onclose:closeHandle});
		//ndn.transport.connectWebSocket(ndn);

		console.log(openHandle);
                console.log('connecting to ws')
                //ndn = new NDN({host:hostip, onopen:openHandle, onclose:closeHandle});
                face = new Face({host:hostip});
                //ndn.transport.connectWebSocket(ndn);
                //ndn.transport.connect(ndn, openHandle);
                face.transport.connect(face, openHandle);

		$(".loader").fadeOut(500, function() {
			if (ospfnRunning) {
				$('.alert-message')
					.append('<div class="alert alert-success">Routing Status loaded <strong>successfully</strong>.</div>')
					.fadeIn(500);
			} else {
				$('.alert-message')
					.append('<div class="alert alert-danger">OSPFN is currently down on <strong>Netlogic</strong>. The information displayed below is <strong>not</strong> up to date.</div>')
					.fadeIn(500);
			}
		});

	});
});


