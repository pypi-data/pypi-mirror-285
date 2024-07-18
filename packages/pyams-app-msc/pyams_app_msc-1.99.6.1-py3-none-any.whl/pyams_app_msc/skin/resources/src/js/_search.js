

const PyAMS_search = {

	updateSort: (evt) => {
		const form = $('form[id="search-results"]');
		if (form.length > 0) {
			const index = $(evt.target).val();
			$('input[name="order_by"]', form).val(index);
			form.submit();
		}
	},

	updatePageLength: (evt) => {
		const form = $('form[id="search-results"]');
		if (form.length > 0) {
			const length = $(evt.target).val();
			$('input[name="start"]', form).val(0);
			$('input[name="length"]', form).val(length);
			form.submit();
		}
	},

	updateSearchFilters: (evt) => {
		const
			urlParams = new URLSearchParams(window.location.search),
			filterTypes = new Set($('input[name="filter"], select[name="filter"]').map((idx, elt) => {
				return $(elt).data('filter-type');
			}).get());
		filterTypes.forEach(type => urlParams.delete(type));
		$('input[name="filter"]:checked, select[name="filter"]').each((idx, elt) => {
			const filterType = $(elt).data('filter-type');
			const value = $(elt).val();
			// Append each selected filter value under its respective filter type
			if (value) {
				urlParams.append(filterType, value);
			}
		});
		// Construct the new URL with updated parameters
		window.location.href = `${window.location.protocol}//${window.location.host}${window.location.pathname}?${urlParams.toString()}`;
	},

	previousPage: (evt) => {
		const form = $('form[id="search-results"]');
		if (form.length > 0) {
			const current = $(evt.target).parents('.pagination').data('ams-current-page');
			const length = $('input[name="length"]', form).val();
			$('input[name="start"]', form).val(length * (current - 2));
			form.submit();
		}
	},

	nextPage: (evt) => {
		const form = $('form[id="search-results"]');
		if (form.length > 0) {
			const current = $(evt.target).parents('.pagination').data('ams-current-page');
			const length = $('input[name="length"]', form).val();
			$('input[name="start"]', form).val(length * current);
			form.submit();
		}
	},

	gotoPage: (evt) => {
		const form = $('form[id="search-results"]');
		if (form.length > 0) {
			const target = parseInt($(evt.target).text());
			const length = $('input[name="length"]', form).val();
			$('input[name="start"]', form).val(length * (target - 1));
			form.submit();
		}
	},

	switchFilter: (evt) => {
		const
			target = $(evt.currentTarget),
			header = $(`[data-toggle="collapse"][href="#${target.attr('id')}"]`);
		$('.fa', header).toggleClass('fa-caret-down').toggleClass('fa-caret-up');
	},

	switchMoreFilters: (evt) => {
		const
			target = $(evt.currentTarget),
			switcher = $(`[data-toggle="collapse"][data-target="#${target.attr('id')}"]`);
		if (target.hasClass('show')) {
			switcher.text(switcher.data('ams-less-label'))
		} else {
			switcher.text(switcher.data('ams-more-label'));
		}
	},

	resetFilters: (evt) => {
		const
			form = $(evt.currentTarget).parents('form');
		$('input[type="checkbox"]', form).prop('checked', false);
		$('select', form).prop('selectedIndex', 0);
		PyAMS_search.updateSearchFilters(evt);
	}
};


export default PyAMS_search;
