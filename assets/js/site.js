/* Highlights the nav entry for the section currently in view.
   The only script on the site; everything else is CSS. */
(function () {
	"use strict";

	var links = Array.prototype.slice.call(
		document.querySelectorAll(".topnav a[href^='#']")
	);
	if (!links.length || !("IntersectionObserver" in window)) return;

	var byId = {};
	var sections = [];

	links.forEach(function (link) {
		var section = document.getElementById(link.hash.slice(1));
		if (!section) return;
		byId[section.id] = link;
		sections.push(section);
	});

	var visible = {};

	function refresh() {
		// The topmost section that is currently on screen wins.
		var current = null;
		for (var i = 0; i < sections.length; i++) {
			if (visible[sections[i].id]) {
				current = sections[i].id;
				break;
			}
		}
		links.forEach(function (link) {
			link.classList.toggle("active", current !== null && link === byId[current]);
		});
	}

	var observer = new IntersectionObserver(
		function (entries) {
			entries.forEach(function (entry) {
				visible[entry.target.id] = entry.isIntersecting;
			});
			refresh();
		},
		// Ignore the strip under the sticky nav, and treat a section as "current"
		// only while a reasonable part of it is in the upper half of the viewport.
		{ rootMargin: "-4.5rem 0px -55% 0px" }
	);

	sections.forEach(function (section) {
		observer.observe(section);
	});
})();
