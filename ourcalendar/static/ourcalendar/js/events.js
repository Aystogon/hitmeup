(function($, $HMU) {
    var events = $HMU.events;

    $(document).ready(function() {

        // Displays the calendar.
        $('#calendar').fullCalendar({
            editable: true,
            header: {
                left: 'prev,next today',
                center: 'title',
                right: 'month,agendaWeek,agendaDay'
            },

            // Shows detail when clicking an event.
            eventClick: function(event) {
                detailReactor.setState({
                    edit: false,
                    title: event.title,
                    location: event.location,
                    description: event.description,
                    start: event.start.format('LLL'),
                    end: event.end.format('LLL'),
                    id: event.id
                });

                // Dev tip: can use event.id to get the clicked event's id
                $('#eventDetailModal').modal('show');
            },
            events: events,
            fixedWeekCount: false,
            height: 600,
            scrollTime: "08:00:00",
            selectable: true,
            eventLimit: true,
            selectHelper: true,
            unselectCancel: "#create-event-modal",
            select: function(start, end) {
                $('#start-picker').data("DateTimePicker").date(start);
                $('#end-picker').data("DateTimePicker").date(end);

                // Reset the state of both the create event modal and the input form.
                creationReactor.setState(creationReactor.getInitialState());
                creationReactor.refs.inputForm.setState(creationReactor.refs.inputForm.getInitialState());

                $("#create-event-modal").modal('show');
            },
            forceEventDuration: true,
            allDaySlot: false,

            eventDrop: function(event, delta, revertFunc)  {
                $.ajax({
                    url: '/api/events/' + event.id + '/',
                    type: "PUT",
                    data: JSON.stringify({
                        start: event.start.format('YYYY-MM-DD HH:mm'),
                        end: event.end.format('YYYY-MM-DD HH:mm')
                    }),
                    contentType: "application/json",
                    success: function (response) {
                    },
                    complete: function () {
                    },
                    error: function (xhr, textStatus, thrownError) {
                        revertFunc();
                        alert("An error occurred, please try again later.");
                        console.log(xhr.responseText);
                    }
                });
            },

            eventResize: function(event, delta, revertFunc)  {
                $.ajax({
                    url: '/api/events/' + event.id + '/',
                    type: "PUT",
                    data: JSON.stringify({
                        start: event.start.format('YYYY-MM-DD HH:mm'),
                        end: event.end.format('YYYY-MM-DD HH:mm')
                    }),
                    contentType: "application/json",
                    success: function (response) {
                    },
                    complete: function () {
                    },
                    error: function (xhr, textStatus, thrownError) {
                        revertFunc();
                        alert("An error occurred, please try again later.");
                        console.log(xhr.responseText);
                    }
                });
            }
        })
    });
})(window.jQuery, window.$HMU);