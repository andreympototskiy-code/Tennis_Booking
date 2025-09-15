(function($) {
    Vue.config.devtools = false;
    Vue.config.productionTip = false;
    /**
     * Менеджер кеша
     */
    var Cache = new (function() {

        this.storage = {};

        this.get = function(name, defaulValue) {
             return this.storage.hasOwnProperty(name) ? this.storage[name] : this.set(name, defaulValue);
        };

        this.set = function(name, value) {
            this.storage[name] = (typeof value == 'function' ? value.call(this) : value);
            return this.storage[name];
        };

    });

    /**
     * Механизм поллинга
     */
    var Poller = window.Poller;

    /**
     * Базовое приложение
     */
    var App = Poller.extend({
        data: function() {
            return {
                is_loaded: false,
                url: {
                    polling: 'polling'
                },
                admin: 0,               // находимся на странице журнала администратора
                court_types: [],        // корты, сгруппированные по дутикам
                inflates: [],           // дутики
                settings: {},           // настройки
                dateString: '',         // строковое представление текущей даты в формате Y-m-d
                dateLocalized: '',      // форматированная строка текущей даты в формате "<число> <месяца>, <день недели>"
                dateLocalizedShort: '', // форматированная строка текущей даты в формате "<число> <месяца>"
                dateToday: 0,           // сегодня
                datePrev: 0,            // возможность пролистать на предыдущую дату
                dateNext: 0,            // возможность пролистать на следующую дату
                dateList: [],           // список дат до конца сезона
                type: 0,                // тип бронирования
                type_seasonal: 0,       // заданный тип бронирования - сезонный
                time_line: 0,           // линия времени (для текущей даты)
                time_list: [],          // список доступного времени
                time_price: [],         // список цен
                time_blocked: [],       // забронированное время
                time_selected: [],      // выбранное время
                discount: 1.0,          // текущая скидка (исходя из типа бронирования и параметров заказа),
                time_stock: [],         // список
                time_trainer: [],
                is_season_booking: false,
                deposit_another_type: [],
                deposit_value: [],
                deposit_stock: null,
                type_deposit: null,
                price_custom: 0,
                discount_old: 1.0,
                diffTime: 0
            };
        },
        computed: {
            // текущая дата как экземпляр momentjs
            date: function() {
                return moment(this.dateString);
            },
            time_order: function() {

                const selected = [];

                _.each(this.time_map, function(court_type) {
                    _.each(court_type.courts, function(court) {
                        _.each(court.groups, function(group) {
                            if (group.selected) {
                                selected.push(group);
                            }
                        });
                    });
                });
                return selected;
            },
            time_map: function() {

                const cells = [];
                const that = this;

                // группируем заказы по кортам и времени
                const blocked = _.groupBy(that.time_blocked, 'court_id');
                // типы кортов
                _.each(that.court_types, function(court_type, court_type_index) {

                    // нормализация списка кортов
                    court_type.courts = _.toArray(court_type.courts);

                    // для каждого типа кортов - список дутиков
                    court_type.inflates = [];

                    // ценовая сетка
                    court_type.price = that.time_price[court_type_index];

                    // идентификатор для кортов без дутиков
                    court_type.negative = -court_type.id * 1000;

                   // let tmp = []
                    // группируем корты по дутикам
                    _.each(court_type.courts, function(court) {

                        if (court.inflate_id === 0) {
                            court.inflate_id = (court_type.id < 3 ? court_type.negative-- : court_type.negative);
                        }

                        const inflate = _.findWhere(court_type.inflates, { id: court.inflate_id })
                            || _.findWhere(that.inflates, { id: court.inflate_id })
                            || { id: court.inflate_id, name: 'откр.', opened: true, courts: [] };

                        _.defaults(inflate, { courts: [] });
                        _.extend(court, { groups: [] });

                        if (_.findIndex(court_type.inflates, { id: inflate.id }) < 0) {
                            court_type.inflates.push(inflate);
                        }

                        if (_.findIndex(inflate.courts, { id: court.id }) < 0) {
                            inflate.courts.push(court);
                        }
                        //Временное хранилище
                       /* if (_.findIndex(tmp, { id: court.id }) < 0) {
                            tmp.push(court)
                        }*/

                        let group;

                        // перебираем временные интервалы
                        _.each(that.time_list, function(time) {

                            var item = _.extend({ // расширяем объект для промежутка времени следующими параметрами
                                id: _.uniqueId('c'),
                                court: court,
                                court_id: court.id,
                                court_type: court_type,
                                court_type_id: court_type.id,
                                type_id: 0,
                                selected: 0,        // выделенная ячейка
                                ordered: 0,         // забронированная ячейка
                                blocked: 0,         // заблокированная по отношению к чужому контексту
                                editable: 0,        // можно модифицировать ячейку
                                movable: 0,         // можно перемещать и растягивать,
                                pasted: 0,          // время прошло
                                pasted_hour: 0,     // время прошло
                                moved: 0,
                                order_id: 0,
                                ordertime_id: 0,
                                ordertime: null,

                                index: 0,           // порядковый номер ячейки внутри тайммэпа
                            }, time);

                            // находим соответствующий ordertime для заданного временного интервала
                            const ordertime = blocked[court.id] && _.find(blocked[court.id], function(item) {
                                    return item.time_from.totalSeconds <= time.time_from.totalSeconds && item.time_to.totalSeconds >= time.time_to.totalSeconds;
                                });

                            const selected = _.find(that.time_selected, function(el) {
                                return el.court_id === item.court_id
                                    && el.time_from === item.time_from.value
                                    && el.time_to === item.time_to.value;
                            });

                            if (ordertime) {
                                _.extend(item, {
                                        order_id: ordertime.order_id,
                                        ordertime_id: ordertime.id,
                                        ordertime: ordertime,
                                        ordered: 1,
                                        moved: ordertime.moved_at
                                    }, ordertime.order && {
                                        type_id: ordertime.type_id || ordertime.order.type_id,

                                        // old value = ordertime.order.type_id > 1 || that.polling.data.type < 2,
                                        editable: ordertime.order.type_id > 3 || that.polling.data.type < 4,
                                        movable: that.polling.data.type < 2 || !ordertime.moved_at
                                    });
                                if (selected) {
                                    that.time_selected = _.without(that.time_selected, selected);
                                }
                            }
                            else if (selected) {
                                _.extend(item, {
                                    selected: 1,
                                    editable: 1,
                                    movable: 1
                                });
                            }


                            if (that.is_season_booking) {
                                item.pasted = false;
                                item.blocked = (item.selected);
                            }
                            else {
                                item.pasted = that.is_past(item.time_to);
                                item.pasted_hour = that.is_past_full(item.time_to);
                                item.blocked = (item.selected || item.ordered) || (!that.admin && item.pasted);
                            }

                            // ставим ячейке индекс рассчитывая его на основании времени, прошедшего с начала дня
                            item.index = (time.time_from.totalSeconds - that.time_list[0].time_from.totalSeconds) / 1800;

                            // если группа уже создана на предыдущей итерации
                            if (group) {
                                if ((item.ordered && item.order_id === group.order_id) || (item.selected && group.selected)) {
                                    item.group = group;// ссылка на родителя но и рекурсия
                                    group.time_to = item.time_to;
                                    group.movable = group.movable && (that.polling.data.type < 2 || !item.moved);
                                    group.items.push(item);// добавляем ячейку в группу
                                    return;
                                }
                            }

                            // создаем группу с уникальным id, зачем-то дублируя поля ячейки, добавляя к ним поле items в которое складываем ячейки
                            group = _.extend({ items: [item] }, item, { id: _.uniqueId('g') });

                            delete group.index;

                            item.group = group;

                            court.groups.push(group);
                        });
                    });

                   /* court_type.inflates = court_type.inflates?.map(i => {
                        let ii = {...i};
                        ii.courts = i.courts.filter(c => ~tmp.findIndex(t => t.number === c.number));
                        return ii;
                    });*/

                    cells.push(court_type);
                });

                return cells;
            },
            time_groups: function() {
                const courts = _.flatten(_.pluck(this.time_map, 'courts'));
                const groups = _.flatten(_.pluck(courts, 'groups'));

                return groups;
            }
        },
        methods: {
            format_price_number: function(number) {
                const str = number.toString().split('').reverse().join('');
                let result = '';
                let arr = [];

                for (let i = 0; i < str.length; i += 3) {
                    arr.push(str.slice(i, i + 3));
                }

                for (let j = 0; j < arr.length; j++) {
                    result += arr[j] + ' ';
                }

                return result.split('').reverse().join('');
            },
            deposit_json: function () {
                return JSON.parse(this.time_edit.type_deposit);
            },
            deposit_calculate: function () {
                const self = this;
                self.deposit_another_type = [];
                self.deposit_value = [];
                $.each($(".dep-input:checked"), function(k, v) {
                    self.deposit_another_type[k] = $(this).val();
                    self.deposit_value[k] = $('input[name="order_deposit['+$(this).val()+']"]').val();
                });
            },
            // не используется
            ckecked_payment: function (time_edit, type, payment) {
                if (type == 8 && payment == 2) {
                    return true;
                }
                if (type != 8 && payment == 1) {
                    return true;
                }
                return false;
            },
            // стандартное форматирование суммы: отбитие тысячных разрядов и отбитие копеек запятыми
            number_format: function (value, decimal) {

                if (typeof decimal != 'number') {
                    decimal = 2;
                }

                value = value.toFixed(decimal).replace(/(\d)(?=(\d{3})+(\.|$))/g, '$1 ');
                value = value.replace('.', ',');

                return value;
            },

            instruction: function (name, data) {
                const that = this;
                if (name === 'add') {
                    _.each(data, function(item, key) {
                        _.each(_.isArray(item) ? item : [item], function(element) {
                            that[key].push(element);
                        });
                    });
                }

                if (name === 'update') {
                    _.each(data, function(item, key) {
                        _.each(_.isArray(item) ? item : [item], function(element) {
                            const index = _.findIndex(that[key], { id: element.id });
                            index > -1 && that.$set(that[key], index, element);
                        });
                    });
                }

                if (name === 'delete' || name === 'remove') {
                    _.each(data, function(item, key) {
                        _.each(_.isArray(item) ? item : [item], function(element) {
                            const index = _.findIndex(that[key], element);
                            index > -1 && that[key].splice(index, 1);
                        });
                    });
                }

                if (name === 'set') {
                    _.each(data, function(item, key) {
                        that.$set(that, key, item);
                    });
                }

                if (name === 'refresh') {
                    that.refresh();
                }
            },
            // не используется
            is_sell: function(index, list) {
                const that = this;
                const hours = list[index].time_from.hours;
                const w  = this.date.format('d');
                if (!['t14.spb.ru', 'local.t14.spb.ru'].includes(that.host)) {
                    return false;
                }
                if (hours == 22 || hours == 23) {
                    return true;
                }
                if ((w == 0 || w == 6) && (hours == 22 || hours == 23 || hours == 21 || hours == 20)) {
                    return true;
                }
                return false;
            },
            is_stock: function (stock) {
                return stock == 1;
            },
            is_last: function(index, list) {
                return index === (list.length - 1);
            },
            is_first: function(index) {
                return index === 0;
            },
            is_after_movable: function(current, list) {
                return current < list.length - 1 && list[current+1].movable || false;
            },
            is_before_movable: function(current, list) {
                return current !== 0 && list[current-1].movable || false;
            },
            is_past_full: function(time) {
                const date = this.date.clone().hour(time.hours).minute(time.minutes).second(time.seconds);

                if (time.minutes === 0) {
                    return date.isBefore(moment().add(30,'minutes'));
                }
                else {
                    return date.isBefore(moment());
                }
            },
            is_past: function(time) {
                const date = this.date.clone().hour(time.hours).minute(time.minutes).second(time.seconds);
                return date.isBefore(moment().add(this.diffTime));
            },

            get_group: function(element) {
                const $element = $(element).filter('[time-group]');
                return $element.length > 0 && _.findWhere(this.time_groups, { id: $element.attr('time-group') }) || null;
            },
            get_cell: function(element) {
                const $element = $(element).filter('[time-cell]'), group = this.get_group($element);
                return $element.length > 0 && group && _.findWhere(group.items, { id: $element.attr('time-cell') }) || null;
            },
            get_price_season: function(time_order) {
                // TODO: интересно что не учитываются как сезонный типы бронирования "группа" и "сезон с разовой оплатой"
                if (this.admin !== 1 || (this.type !== 2 && this.type !== 12)) {
                    return this.get_price(time_order);
                }

                let response;
                const that = this;

                const type_id = this.type;
                // после 2024-09-01 дефолтная скидка для сезонных типов бронирования становится 10% а не 20%
                const discount = this.date.isSameOrAfter('2024-09-01') ? 0.90 : 0.80;

                const data = {
                    date: that.dateString,
                    ordertime: {

                    },
                    order: {
                        type_id: type_id,
                        discount: discount,
                    }
                };

                // TODO: discount захардкожен здесь а не берется из селекта, а это неправильно

                _.each(time_order,  function(item, index) {
                    data['ordertime'][index] = {
                        'court_id': item.court_id,
                        'time_from': item.time_from.value,
                        'time_to': item.time_to.value
                    }
                });

                $.ajax({
                    url: that.ajaxform_get_price_url,
                    method: 'POST',
                    data: data,
                    async: false,
                    success: function(resp) {
                        response = resp;
                    },
                });

                return response;
            },
            get_price: function(group, deposit_another_type) {
                const self = this;
                const type = this.type;
                const stock_color = this.stock_color;
                const trainer_color = this.trainer_color;
                const that = this;
                const dates = this.type_seasonal && this.settings.dates || 1;
                let discount = this.discount;

                if (type === 9) {
                    discount = 0;
                }

                let price_detail = 0;
                const price = _.reduce(_.isArray(group) ? group : [group], function(price, item) {

                    const time_from = item.time_from;
                    const time_to = item.time_to;
                    let index_from = 0;
                    let index_to = 0;

                    _.each(that.time_list, function(time, index) {
                        if (time.time_from.value === time_from.value) {
                            index_from = index;
                        }
                        if (time.time_to.value === time_to.value) {
                            index_to = index;
                        }
                    });
                    _.each(item.court_type.price, function(time_price, index) {
                        if (index >= index_from && index <= index_to) {
                            // если нажат чекбокс "сумма вручную", сумму берем оттуда
                            if (that.price_custom_type) {
                                price = Number(that.price_custom);
                            }
                            // если не нажат чекбокс "сумма вручную"
                            else {
                                // если отмечены чекбоксы .dep-input которые есть во views/order_table.tpl но закомментированы
                                // т.е эта ветка сейчас не выполняется
                                if (that.deposit_another_type.length) {
                                    $.each(that.deposit_another_type, function (k, v) {
                                        if (v === '6') {
                                            price += Number(that.get_money_is_color(that.deposit_value[k]) / 2);
                                        }
                                        if (v === '7') {
                                            // для Тухачевского с 1 сентября по 31 января для индивидуальных занятий с тренером для 1/2/3 человек стоимость рассчитывается как не "тренер+корт", а как только "тренер"
                                            if (['t14.spb.ru', 'local.t14.spb.ru'].includes(self.host) && that.deposit_value[k] !== '#0b3dff' && moment().isAfter('2022-08-31') && moment().isBefore('2023-02-01')) {
                                                price += Number(that.get_money_is_color_trainer(that.deposit_value[k]) / 2);
                                            }
                                            else {
                                                price += time_price;
                                                price_detail += Number(that.get_money_is_color_trainer(that.deposit_value[k]) / 2);
                                            }
                                        }
                                    })
                                }
                                else {
                                    if (type === 6) { // акция
                                        price += Number(that.get_money_is_color(stock_color) / 2);// цена за акцию за полчаса
                                    }
                                    else if (type === 7) { // тренер
                                        // для Тухачевского с 1 сентября по 31 января для индивидуальных занятий с тренером для 1/2/3 человек стоимость рассчитывается как не "тренер+корт", а как только "тренер"
                                        if (['t14.spb.ru', 'local.t14.spb.ru'].includes(self.host) && trainer_color !== '#0b3dff' && moment().isAfter('2022-08-31') && moment().isBefore('2023-02-01')) {
                                            price += Number(that.get_money_is_color_trainer(trainer_color) / 2);
                                        }
                                        else {
                                            price += time_price;// цена за корт
                                            price_detail += Number(that.get_money_is_color_trainer(trainer_color) / 2);// цена за тренера за полчаса
                                        }
                                    }
                                    else if (type === 12) { // сезон с тренером
                                        price += time_price;// цена за корт
                                        // при создании заказа в типе "сезон с тренером" тренера нет поэтому price_detail не расписываем
                                        // price_detail += Number(that.get_money_is_color_trainer(trainer_color) / 2);// цена за тренера за полчаса
                                    }
                                    else {
                                        price += time_price;// по дефолту цена за корт
                                    }
                                }

                            }
                        }

                    });
                    return price;

                }, 0);

                return Math.round(price * discount + price_detail);// скидку делаем от цены за корт; от цены за тренера скидку не делаем
            },
            // округляем цену
            number_convert: function(value) {
                return Math.round(value);
            },
            // возвращаем цену тренера по его цвету
            get_money_is_color_trainer: function(color) {
                const moneys = this.settings.money;
                const colors = this.settings.color;
                let money = 0;
                $.each(colors, function (k, v) {
                    if (!k.indexOf('trainer') && v === color) { // если среди всего массива настроек цвета, которые для тренеров, нашли цвет, совпадаюший с заданным
                        return money = moneys[k];// присваиваем и сразу возвращаем, прерывая перебор
                    }
                });
                if (money) { // если изменились с 0
                    return money;
                }
                return moneys['trainer1'];// иначе возвращаем цену первого тренера в списке
            },
            // возвращаем цену акции по её цвету
            get_money_is_color: function(color) {
                const moneys = this.settings.money;
                const colors = this.settings.color;
                let money = 0;
                $.each(colors, function (k,v) {
                    if (!k.indexOf('stock') && v === color) {
                        return money = moneys[k];
                    }
                });
                if (money) {
                    return money;
                }
                return moneys['stock1'];
            },
            // сумма за месяц для сезонных заказов в режиме редактирования
            get_price_month: function(times, ordertime) {

                const month = moment(ordertime.date_at).month();
                const discount = this.discount;
                const price = times.reduce(
                    function (accumulator, time) {
                        if ((time.delete_sharing || !time.deleted_at) && month === moment(time.date_at).month()) {
                            accumulator += Math.ceil((time.price - parseInt(time.price_detail)) * discount + parseInt(time.price_detail));
                        }
                        return accumulator;
                    }, 0);

                return price;
            },
            get_hours: function(group) {
                return (group.time_to.totalSeconds - group.time_from.totalSeconds)/3600;
            },

            get_selection: function(cell) {
                return {
                    court_id: cell.court_id,
                    time_from: cell.time_from.value,
                    time_to: cell.time_to.value
                };
            },
            select: function(cell) {
                _.isArray(cell) ? _.each(cell, this.select, this) : this.time_selected.push(this.get_selection(cell));
            },
            unselect: function(cell) {
                _.isArray(cell) ? _.each(cell, this.unselect, this) : this.time_selected = _.reject(this.time_selected, this.get_selection(cell));
            },
            unselect_all: function() {
                this.time_selected = [];
            },
            clear_price_custom: function() {
                this.price_custom = 0;
                this.price_custom_type = 0;
            },
            highlight: function(element) {
                $(element).closest('.timemap__group').addClass('highlight');
            },
            unhighlight: function(element) {
                $(element).closest('.timemap__group').removeClass('highlight');
            },

            handle_click: function(cell, event) {
                if (cell.ordered) {
                    return;
                }
                if (this.admin) {
                    this[cell.selected ? 'unselect' : 'select'](cell);
                }
                else if (cell.pasted) {
                    return;
                }
                else {
                    const siblings = _.flatten(_.pluck(cell.court.groups, 'items'));
                    let prev = _.find(siblings, function(item) {
                        return item.time_to.value === cell.time_from.value;
                    });
                    let next = _.find(siblings, function(item) {
                        return item.time_from.value === cell.time_to.value;
                    });
                    if (cell.selected) {
                        if (cell.group.items.length < 3) {
                            cell = cell.group.items;
                        }
                        else {
                            const cell_index = _.findIndex(cell.group.items, { id: cell.id });
                            if (cell_index === 1) {
                                cell = cell.group.items.length === 3 ? cell.group.items : _.first(cell.group.items, 2);
                            }
                            else if (cell_index === cell.group.items.length - 2) {
                                cell = _.last(cell.group.items, 2);
                            }
                        }
                        this.unselect(cell);
                    }
                    else {
                        var next_selected = next ? next.selected : 0;
                        var prev_selected = prev ? prev.selected : 0;
                        if (!next_selected && !prev_selected) {
                            next = next && next.blocked ? null : next;
                            prev = prev && prev.blocked ? null : prev;
                            cell = _.filter([cell, next || prev]);

                            if (cell.length < 2) {
                                return;
                            }
                        }
                        this.select(cell);
                    }
                }
                if (event) {
                    event.preventDefault();
                    event.stopPropagation();
                }
            },

            order_background: function() {
                return this.get_color_background.apply(this, arguments);
            },
            order_bound: function() {
                return this.get_color_border.apply(this, arguments);
            },
            order_text: function() {
                return this.get_color_text.apply(this, arguments);
            },
            // цвет фона группы заказа
            get_color_background: function(group) {
                let tid = 0;
                let tname = '';
                if (_.isObject(group)) {
                    if (group.ordered) { // если группа = заказ
                        if (group.ordertime.order && group.ordertime.order.color) {
                            return group.ordertime.order.color;// если у заказа есть цвет - возвращаем его. но почему-то у заказов нет цветв
                        }

                        if (group.type_id && group.type_id === 12 && group.ordertime.trainer_color) {
                            // this.settings.color['season-train'] - цвет сезона с тренером
                            // group.ordertime.trainer_color - цвет тренера
                            const type_color = this.settings.color['season-train'];
                            const trainer_color = group.ordertime.trainer_color;
                            return `linear-gradient(to bottom, ${type_color}, ${type_color} 50%, ${trainer_color} 50%, ${trainer_color})`;
                        }

                        tid = group.type_id;// tid = номер типа группы
                    }
                }
                else if (/^\d+$/g.test(group)) { // если группа почему-то состоит из только номера
                    tid = parseInt(group);// tid = номер
                }
                else { // если группа - свободное время
                    tname = group;
                }

                if (tid) { // если есть
                    tname = {
                        1: 'once',
                        2: 'season',
                        3: 'group',
                        4: 'tourney',
                        5: 'season-once',
                        6: 'stock',
                        7: 'trainer',
                        8: 'deposit',
                        9: 'closed',
                        10: 'club',
                        11: 'club-once',
                        12: 'season-train',
                    }[tid];
                }
                if (this.settings.color) {
                    return this.settings.color[tname];
                }

                return '';
            },
            // цвет фона ручек, за которые можно растягивать группы заказа
            get_color_border: function(group) {

                let background;

                if (group.type_id && group.type_id === 12 && group.ordertime.trainer_color) {
                    background = this.settings.color['season-train'];
                }
                else {
                    background = this.get_color_background(group);
                }

                if (background) {
                    if (window.tinycolor) {
                        return Cache.get('color.bound.' + (background || 'none'), function() {
                            const bg = window.tinycolor(background);
                            const bc = bg.isDark() ? bg.lighten(30).toString() : bg.darken(15).toString();
                            return bc;
                        });
                    }
                }

                return '';
            },
            // цвет текста группы заказа
            get_color_text: function(group) {

                let background;

                if (group.type_id && group.type_id === 12 && group.ordertime.trainer_color) {
                    background = this.settings.color['season-train'];
                }
                else {
                    background = this.get_color_background(group);
                }

                if (background) {
                    if (window.tinycolor) {
                        return Cache.get('color.text.' + (background || 'none'), function() {
                            const colors = Cache.get('color.all', function() {
                                let items = [];
                                for (const i in window.tinycolor.names) {
                                    items.push(window.tinycolor.names[i]);
                                }
                                return items;
                            });
                            const bg = window.tinycolor(background);
                            const tc = window.tinycolor.mostReadable(bg, colors).toString();
                            return tc;
                        });
                    }
                }

                return '';
            },

            refresh: function() {
                this.polling_data({ timestamp: 0 });
            },
            update: function(params) {
                const that = this;
                const url = this.absolute(this.url.polling);
                params = $.extend({ date: this.date , type: this.type }, params);

                $.ajax({
                    type: 'get',
                    url: url,
                    data: { date: params.date.format('YYYY-MM-DD'), type: params.type },
                    dataType: 'json',
                    cache: false,
                    timeout: 5000,
                    async: true,
                    success: function(response) {
                        that.done(response);
                    }
                });
            },
            date_goto: function(date) {
                this.unselect_all();
                if (this.polling_running()) {
                    this.polling_data({ date: date.format('YYYY-MM-DD'), timestamp: 0 });
                    this.polling_stop();
                    this.polling_start();
                }
                else {
                    this.polling_data({ date: date.format('YYYY-MM-DD'), timestamp: 0 });
                    this.update({ date: date });
                }
            },
            date_next: function() {
                this.date_goto(this.date.clone().add(1, 'days'));
            },
            date_prev: function() {
                this.date_goto(this.date.clone().subtract(1, 'days'));
            },
            date_today: function() {
                if (!this.dateToday) {
                    this.date_goto(moment());
                }
            },
            // обертка для moment.js
            moment: function() {
                return window.moment && window.moment.apply(this, arguments);
            },
            order_submit: function(trigger, test) {
                test = test||false;

                const form = $(trigger).closest('form');
                let url = form.attr('action');
                const data = form.serialize();

                if (test) {
                    url = url + "?test_payment=1";
                }

                this.form(url, data, 'post');
            }
        },
        created: function() {
            if (!this.dateToday) {
                this.is_loaded = true;
            }

            this.$on('done', function(response) {
                if (response.instructions) {
                    _.each(response.instructions, function(item, key) {
                        this.instruction(key, item);
                    }, this);
                }
            });
        },
        watch: {
            date: function(value) {
                if (History) {
                    History.pushState(null, document.title, '?date=' + value.format('YYYY-MM-DD'));
                }
            },
            dateToday: function(value) {
                const self = this;
                const header = $('.timemap__header--time .timemap__row--first').first();
                const content = $('.content');
                let line = $('.timeline', header);
                const handle = self.time_line_handle;

                self.time_line = false;

                if (handle) {
                    clearInterval(handle);
                }

                if (value) {

                    if (line.length === 0) {
                        if (!self.is_season_booking) {
                            line = $('<div class="timeline" title="Текущее время"><div class="timeline__text"></div></div>');
                            line.appendTo(header);
                        }
                    }

                    const secondsMin = _.first(this.time_list).time_from.totalSeconds;// начало тайммэпа в секундах
                    const secondsMax = _.last(this.time_list).time_to.totalSeconds;// конец тайммэпа в секундах

                    let serverOffset = 0;
                    $.ajax({
                        url: '/bronirovanie/time_now/',
                        method: 'GET',
                        success: function(r) {
                            self.tz = r.tz;
                            serverOffset = moment(r.server_time * 1000).diff(new Date());
                            self.time_line_handle = setInterval((function(callback) { callback.call(); return callback; })(function() {
                                self.is_loaded = true;
                                let now;
                                if (serverOffset) {
                                    now = moment().add(serverOffset, 'milliseconds');
                                }
                                else {
                                    now = moment();
                                }
                                // корректировка временной зоны
                                const curTz = new Date().getTimezoneOffset();
                                self.diffTime = (curTz * 60 + r.tz) * 1000;
                                now.add(self.diffTime, 'milliseconds');

                                // const seconds = now.hours()*3600 + Math.floor(now.minutes()/30)*30*60 + 0;
                                let offset = 0;
                                if (['t14.spb.ru', 'local.t14.spb.ru'].includes(self.host)) {
                                    if (self.module === 'widget') {
                                        offset = 5;
                                    }
                                    if (self.module === 'admin') {
                                        offset = 15;
                                    }
                                }

                                if (['x19.spb.ru', 'local.x19.spb.ru'].includes(self.host)) {
                                    offset = 45;
                                    if (self.module === 'widget') {
                                        offset = 25;
                                    }
                                }

                                const seconds = now.hours() * 3600 + now.minutes() * 60 + now.seconds();
                                const left = -line.outerWidth()/2 + ( header.outerWidth() - offset ) * (seconds - secondsMin) / (secondsMax - secondsMin);
                                self.time_line = left;

                                line.css({
                                    top: '-10px',
                                    left: left + 'px',
                                    height: content.outerHeight() + 20
                                });

                                $('.timeline__text', line).html(now.format('HH:mm'));

                                // if (self.module === 'widget' && document.getElementById('logic-loading') !== null) {
                                //     document.getElementById('logic-loading').remove();
                                // }

                            }), 5000);
                        }
                    });

                    let percentOfDayRangeComplete = function(start, end) {
                        const now = moment().add(self.diffTime, 'milliseconds');
                        start = start || moment(now).startOf('day');
                        end = end || moment(now).endOf('day');
                        const totalMillisInRange = end.valueOf() - start.valueOf();
                        const elapsedMillis = now.valueOf() - start.valueOf();
                        // This will bound the number to 0 and 100
                        return Math.max(0, Math.min(100, 100 * (elapsedMillis / totalMillisInRange)));
                    };
                    $(document).ready(function() {
                        // Handler for .ready() called.
                        setTimeout(function() {
                            $('.app_widget_t14').animate({
                                scrollLeft: (250/100 * percentOfDayRangeComplete()) + 80,
                            }, 'slow');
                        }, 500);
                    });

                    $(document).ready(function () {
                        // Handler for .ready() called.
                        setTimeout(function() {
                            $('.app_t14 .block-inline_wrapper').animate({
                                scrollLeft: (440/100 * percentOfDayRangeComplete()) + 80,
                            }, 'slow');
                        }, 500);
                    });



                }
                else {
                    line.remove();
                    $(document).ready(function() {
                        // Handler for .ready() called.
                        setTimeout(function() {
                            $('.app_widget_t14').animate({
                                scrollLeft: 0,
                            }, 'slow');
                        }, 500);
                    });

                    $(document).ready(function() {
                        // Handler for .ready() called.
                        setTimeout(function() {
                            $('.app_t14 .block-inline_wrapper').animate({
                                scrollLeft: 0,
                            }, 'slow');
                        }, 500);
                    });
                }
            },
            // при смене типа заказа меняем скидку для заказа
            type: function(newValue, oldValue) {
                this.unselect_all();
                this.discount = this.settings.discount && this.settings.discount[this.type] || 1;
            }
        },
        updated: function() {
            const that = this;
            const jWindow = $(window);
            const jBody = $(document.body);
            const jContent = $('.content', this.$el);

            function getCell(left, top, container) {
                const elements = atPoint(left + jWindow.scrollLeft() + 1, top - jWindow.scrollTop(), container);// atPoint - библиотека с 006
                let cell;
                $(elements).each(function(i, el) {
                    const jEl = $(el);
                    if (jEl.closest('.ui-draggable-dragging').length === 0) {
                        if (jEl.hasClass('timemap__handle')) {
                            cell = jEl;
                        }
                    }
                });
                return cell;
            }

            function getGroup(cell) {
                return $(cell).closest('.timemap__group');
            }

            function getSiblings(cell, direct) {
                const cells = [];
                const after = (direct !== 'before');
                cell[after ? 'nextAll' : 'prevAll']('.timemap__handle').each(function(i, el) {
                    cells.push(el);
                });
                getGroup(cell)[after ? 'nextAll' : 'prevAll']('.timemap__group').each(function(i, group) {
                    const groupCells = $('.timemap__handle', group).toArray();
                    $(after ? groupCells : groupCells.reverse()).each(function(j, el) {
                        cells.push(el);
                    });
                });
                return $(cells);
            }

            function getBefore(cell, count) {
                const cells = getSiblings(cell, 'before');
                return (typeof count !== 'undefined' ? cells.slice(0, count) : cells);
            }

            function getAfter(cell, count) {
                const cells = getSiblings(cell, 'after');
                return (typeof count !== 'undefined' ? cells.slice(0, count) : cells);
            }

            function getUntil(from, to, direct) {
                let cells = $([]);
                getSiblings(from, direct).each(function(i, el) {
                    cells = cells.add(el);
                    if ($(el).attr('time-cell') === $(to).attr('time-cell')) {
                        return false;
                    }
                });
                return cells;
            }

            function getAfterUntil(from, to) {
                return getUntil(from, to, 'after');
            }

            function getBeforeUntil(from, to) {
                return getUntil(from, to, 'before');
            }

            // проверка, свободно ли время, на которое перемещаем/растягиваем заказ
            function validateFreeTime(data, callback_if_success, callback_if_fail) {
                let formData = new FormData();
                formData.append('ordertime', JSON.stringify(data));

                fetch(
                    that.absolute(that.url.ordertime_validate), {
                        method: 'POST',
                        body: formData,
                    }
                )
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.success) {
                            callback_if_success();
                        }
                        else {
                            callback_if_fail(data.dates);
                        }
                    })
                    .catch(error => console.error(error));
            }

            /**
             * показывает модальное окно с занятыми датами при неудачной попытке изменения времени
             * @param dates
             */
            function showOccupiedDatesModal(dates) {
                const dates_string = dates.map((date) => {
                    const moment_date = moment(date);
                    return '<span style="white-space: nowrap;">' + moment_date.date()+' '+that.months_arr[moment_date.month()] + '</span>';
                });

                const jModal = that.dialog({
                    title: 'Нельзя изменить параметры бронирования',
                    message: '<div class="text-center">Новое время занято в следующие даты: ' + dates_string.join(', ') + '</div>',
                });
            }

            /**
             * Вешаем обработчики на ячейки
             */
            $('.timemap__body--time', this.$el).each(function(index, body) { // на каждый ряд с ячейками времени

                if (typeof $.fn.draggable === 'undefined') {
                    return;
                }

                // Строка с ячейками
                const jBody = $(body);

                // Все ячейки
                const jCell = jBody.find('.timemap__cell');


                // Ширина и высота одной ячейки
                const width = jCell.outerWidth();
                const gridX = jCell.outerWidth();
                const gridY = jCell.outerHeight();


                // Группы ( Ячейки и выбранные периоды )
                const jGroups = jBody.find('.timemap__group');// если ячейка невыбрана - ячейка, если ячейка выбрана - период

                // Ячейки которые перерисовывались
                const jUpdated = jGroups.filter('.updated');

                // Выбранные
                const jSelected = jUpdated.filter('.selected');

                // Заказанные
                const jOrdered = jUpdated.filter('.ordered');

                // Заблокированные
                const jBlocked = jUpdated.filter('.blocked');

                // Те что можно двигать
                const jMovable = jUpdated.filter('.movable');

                // Свободные
                const jFree = jUpdated.filter('.free');

                // Горизонтальные
                const isHorizontal = jBody.closest('.timemap').hasClass('timemap--horizontal');

                // Снятие предрасположенности к перетаскиванию
                jUpdated.draggable().draggable('destroy');


                // Добавление предрасположенности к перетаскиванию
                jMovable.draggable({
                    containment: jContent,
                    cursor: 'move',
                    snap: '.timemap__group',
                    snapMode: 'both',
                    delay: 200,

                    start: function(event, ui) {
                        $(this).addClass('timemap__type--dragging');
                    },

                    // Событие на завершение перетаскивания
                    stop: function(event, ui) {

                        $(this).removeClass('timemap__type--dragging');

                        // схваченная группа
                        const jSourceGroup = $(this);

                        // первая ячейка в наборе в месте на которое перетаскиваем
                        const jTargetFrom = getCell(ui.offset.left + 3, ui.offset.top + 3, body);

                        if (!jTargetFrom) {
                            return;
                        }

                        // схваченная группа как объект со всеми ссылками
                        const source = that.get_group(jSourceGroup);

                        // набор ячеек в месте, на которое перетаскиваем группу длиной равной длине схваченной группы
                        const jTargetCells = jTargetFrom.add(getAfter(jTargetFrom, source.items.length - 1));

                        // последняя ячейка в наборе в месте на которое перетаскиваем
                        const jTargetTo = jTargetCells.last();

                        /**
                         * На заблокированные и выделенные ячейки не можем перемещать элементы
                         * верно только для текущего дня
                         */
                        const jTargetBlocked = jTargetCells.filter(function(i, cell) {
                            const jCell = $(cell);
                            const jGroup = jCell.closest('.timemap__group');// группа к которой относится ячейка
                            if (jGroup.attr('time-group') === jSourceGroup.attr('time-group')) { // если текущая группа - не в счёт
                                return false;
                            }
                            return jGroup.hasClass('blocked');// оставляем если для ячейки группа имеет класс blocked
                        });

                        if (jTargetBlocked.length > 0) {
                            return;
                        }

                        /**
                         * Новое время
                         */
                        const targetFrom = that.get_cell(jTargetFrom);// первая ячейка в наборе в месте на которое перетаскиваем как объект со всеми ссылками
                        const targetTo = that.get_cell(jTargetTo);// последняя ячейка в наборе в месте на которое перетаскиваем как объект со всеми ссылками

                        const timeFrom = targetFrom.time_from;// время начала для первой ячейки в наборе как объект
                        const timeTo = targetTo.time_to;// время конца для последней ячейки в наборе как объект

                        function resumeSelectedMove() {
                            let select = [];
                            const unselect = [];

                            jTargetCells.each(function(i, el) {
                                select.push(that.get_cell(el));
                            });

                            _.each(source.items, function(item) {
                                if (_.findIndex(select, { id: item.id }) < 0) {
                                    unselect.push(item);
                                }
                            });

                            select = _.reject(select, { selected: 1 });

                            that.unselect(unselect);
                            that.select(select);
                        }

                        function resumeOrderedMove() {
                            that.highlight(jTargetCells);

                            const jModal = that.dialog({ // вроде как обертка для модального окна из bootstrap 3.3.7
                                title: 'Бронирование',
                                message: '<div class="text-center">Переместить выбранный заказ на новое время (с ' +timeFrom.title+ ' по ' +timeTo.title+ ')<br/>на ' +targetTo.court_type.name+ ' №' +targetTo.court.number+ '?</div>',
                                buttons: {
                                    'Переместить': function() {
                                        that.post(that.url.ordertime_move, {
                                            ordertime: {
                                                id: source.ordertime_id,
                                                court_id: targetFrom.court_id,// передаем номер корта но не используем его на стороне сервера
                                                time_from: timeFrom.title,
                                                time_to: timeTo.title
                                            },
                                            type: that.type,
                                        });
                                        jModal.modal('hide');
                                    }
                                }
                            });

                            jModal.on('hide.bs.modal', function() {
                                that.unhighlight(jTargetCells);
                            });
                        }

                        /**
                         * Перемещение выделенного участка
                         */
                        if (source.selected) { // если работаем не с созданной группой, а с выделением

                            // проверяем, заняты ли ячейки, на которые переносим, в другие даты
                            // только если новый заказ сезонный
                            if ([2, 3, 5, 12].includes(that.type)) {
                                const ordertime = {
                                    order_id: 0,// поскольку заказа еще нет то номера заказа тоже нет
                                    date_at: that.dateString,// дата на которой стоим
                                    court_id: targetFrom.court_id,// id корта
                                    time_from: timeFrom.title,// время с (ex: 11:00)
                                    time_to: timeTo.title,// время до (ex: 14:00)
                                }

                                validateFreeTime(ordertime, resumeSelectedMove, showOccupiedDatesModal);
                            }
                            else {
                                resumeSelectedMove();
                            }
                        }

                        /**
                         * Перемещение заказов
                         */
                        if (source.ordered) { // если работаем с созданной группой

                            // проверяем, заняты ли ячейки, на которые переносим, в другие даты
                            // только если тип заказа сезонный и режим редактирования заказа сезонный
                            // потому что если редактировать сезонный заказ в режиме "разово" то редактируется только текущая дата
                            if ([2, 3, 5, 12].includes(source.type_id) && [2, 3, 5, 12].includes(that.type)) {
                                const ordertime = {
                                    order_id: source.order_id,// номер заказа для контроля выборки
                                    date_at: that.dateString,// дата на которой стоим
                                    court_id: targetFrom.court_id,// id корта
                                    time_from: timeFrom.title,// время с (ex: 11:00)
                                    time_to: timeTo.title,// время до (ex: 14:00)
                                }

                                validateFreeTime(ordertime, resumeOrderedMove, showOccupiedDatesModal);
                            }
                            else {
                                resumeOrderedMove();
                            }
                        }
                    },
                    helper: 'clone',
                });

                jMovable.each(function(i, el) {
                    const jGroup = $(el);// группа
                    const jRow = jGroup.closest('.timemap__row');// ряд, к которому относится группа
                    const jAfter = $('.timemap__after', jGroup);// граница последней ячейки группы, за которую можно тянуть
                    const jBefore = $('.timemap__before', jGroup);// граница первой ячейки группы, за которую можно тянуть
                    const jGroupCells = jGroup.find('.timemap__cell');// ячейки в группе
                    const jGroupCellFirst = jGroupCells.first();// первая ячейка группы
                    const jGroupCellLast = jGroupCells.last();// последняя ячейка группы
                    const jGroupNext = $(jGroupCellLast).add(jGroup.nextUntil('.blocked')).last();// последняя незанятая ячейка до следующей занятой
                    const jGroupPrev = $(jGroupCellFirst).add(jGroup.prevUntil('.blocked')).first();// первая незанятая ячейка после предыдущей занятой
                    const group = that.get_group(jGroup);// группа как объект со всеми ссылками

                    // Логика для боковых элементов группы
                    function makeDraggable(jHandler, direct) {
                        const after = (direct !== 'before');// bool направление (вперед - true)
                        let containment = [];


                        // свободное место для передвижения
                        if (after) {
                            containment = [
                                jGroupCellFirst.offset().left - width, jGroupCellFirst.offset().top,
                                jGroupNext.offset().left + jGroupNext.outerWidth(), jGroupNext.offset().top + jGroupNext.outerHeight()
                            ];// прямоугольник от предыдущей ячейки перед группой до последней ячейки в свободном месте после группы. TODO: как будто бы одна ячейка слева лишняя
                        }
                        else {
                            containment = [
                                jGroupPrev.offset().left - 1, jGroupPrev.offset().top,
                                jGroupCellLast.offset().left + width, jGroupCellLast.offset().top + jGroupCellLast.outerHeight()
                            ];// прямоугольник от первой ячейки в свободном месте до группы до последней ячейки группы
                        }

                        jHandler.draggable({
                            containment: containment,// типа место, в котором ее можно перетаскивать
                            grid: [gridX, 0],
                            axis: isHorizontal ? 'x' : 'y',// направление перетаскивания в зависимости от того, как расположена сетка - горизонтально или вертикально
                            stop: function(event, ui) { // в момент остановки выполняем

                                if (ui.position.left === ui.originalPosition.left && ui.position.top === ui.originalPosition.top) {
                                    return;// если никуда не передвинули - отмена
                                }

                                const length = jGroup.find('.timemap__cell').length - 1;// количество ячеек в группе

                                if (length * 26 === ui.position.left && !after) {
                                    return;
                                } // по идее если двигаем вправо и дошли до конца - отмена, но вроде бы повесили на направление влево
                                if (ui.position.left === 21 && after) {
                                    return;
                                } // по идее если двигаем влево и дошли до начала - отмена, но вроде бы повесили на направление вправо

                                const jCellFrom = jGroup.find('.timemap__cell')[after ? 'last' : 'first']();// последняя или первая ячейка группы в зависимости от направления перетаскивания
                                const jCellTo = getCell(ui.offset.left + 3, ui.offset.top + 3, body);// ячейка в которой остановились

                                const cell_from = that.get_cell(jCellFrom);// последняя или первая ячейка группы как объект со всеми ссылками
                                const cell_to = that.get_cell(jCellTo);// ячейка в которой остановились как объект со всеми ссылками
                                const cell_increase = (after ? 1 : -1) * (cell_to.time_from.totalSeconds - cell_from.time_from.totalSeconds);// дельта секунд на которые раздвигаем группу - положительная или отрицательная в зависимости от направления перетаскивания
                                if (cell_increase === 0) { // если дельта секунд равна 0 - отмена
                                    return;
                                }

                                // ячейки которые нужно добавить или убрать
                                const jCells = (after ? getAfterUntil : getBeforeUntil).apply(this, cell_increase > 0 ? [jCellFrom, jCellTo] : [jCellTo, jCellFrom]);


                                to = cell_to.time_from.totalSeconds - cell_from.time_from.totalSeconds;// дельта секунд на которые раздвигаем группу
                                from = cell_to.time_to.totalSeconds - cell_from.time_to.totalSeconds;// дельта секунд на которые раздвигаем группу

                                // ячейки которые нужно добавить или убрать как объекты
                                const cellsToChange = jCells.toArray().map(function(el) {
                                    return that.get_cell(el);
                                });

                                function resumeSelectedStretch() {
                                    const cellsInGroup = jGroup.find('.timemap__cell').toArray().map(function(el) { // ячейки которые изначально в выделении как объекты
                                        return that.get_cell(el);
                                    });

                                    if (cell_increase < 0 && (cellsInGroup.length - cellsToChange.length) === 1) { // если сужаем и в результате изменения остается одна ячейка - отмена
                                        return;
                                    }

                                    that[cell_increase > 0 ? 'select' : 'unselect'](cellsToChange);
                                }

                                function resumeOrderedStretch() {
                                    that.highlight(jCells);
                                    const timeFrom = after ? group.time_from : cell_to.time_from;
                                    const timeTo = after ? cell_to.time_to : group.time_to;
                                    if (timeFrom.title === timeTo.title) {
                                        return;
                                    }
                                    const jModal = that.dialog({
                                        title: 'Бронирование',
                                        message: '<div class="text-center">Задать новое время (с ' + timeFrom.title + ' по ' + timeTo.title + ') для выбранного заказа?</div>',
                                        buttons: {
                                            'Задать': function() {
                                                that.post(that.url.ordertime_stretch, {
                                                    ordertime: { // не передаем номер корта потому что растягиваем только внутри одного корта
                                                        id: group.ordertime_id,
                                                        time_from: timeFrom.title,
                                                        time_to: timeTo.title
                                                    },
                                                    type: that.type, // по умолчанию всегда 1
                                                });
                                                jModal.modal('hide');
                                            }
                                        }
                                    });

                                    jModal.on('hide.bs.modal', function() {
                                        that.unhighlight(jCells);
                                    });
                                }

                                /**
                                 * Растягивание/сжатие выделенного участка
                                 */
                                if (group.selected) { // если работаем не с созданной группой, а с выделением

                                    // проверяем, заняты ли ячейки, на которые раздвигаем, в другие даты
                                    // только если новый заказ сезонный и раздвигаем время
                                    if ([2, 3, 5, 12].includes(that.type) && cell_increase > 0) {
                                        const ordertime = {
                                            order_id: 0,// поскольку заказа еще нет то номера заказа тоже нет
                                            date_at: that.dateString,// дата на которой стоим
                                            court_id: cellsToChange[0].court_id,// id корта
                                            time_from: cellsToChange[0].time_from.title,// время с (ex: 11:00)
                                            time_to: cellsToChange[cellsToChange.length - 1].time_to.title,// время до (ex: 14:00)
                                        }

                                        validateFreeTime(ordertime, resumeSelectedStretch, showOccupiedDatesModal);
                                    }
                                    else {
                                        resumeSelectedStretch();
                                    }
                                }

                                /**
                                 * Растягивание/сжатие заказов
                                 */
                                if (group.ordered) { // если работаем с созданной группой

                                    // проверяем, заняты ли ячейки, на которые раздвигаем, в другие даты
                                    // только если тип заказа сезонный и режим редактирования заказа сезонный и раздвигаем время
                                    // потому что если редактировать сезонный заказ в режиме "разово" то редактируется только текущая дата
                                    if ([2, 3, 5, 12].includes(group.type_id) && [2, 3, 5, 12].includes(that.type) && cell_increase > 0) {
                                        const ordertime = {
                                            order_id: group.order_id,// номер заказа для контроля выборки
                                            date_at: that.dateString,// дата на которой стоим
                                            court_id: cellsToChange[0].court_id,// id корта
                                            time_from: cellsToChange[0].time_from.title,// время с (ex: 11:00)
                                            time_to: cellsToChange[cellsToChange.length - 1].time_to.title,// время до (ex: 14:00)
                                        }

                                        validateFreeTime(ordertime, resumeOrderedStretch, showOccupiedDatesModal);
                                    }
                                    else {
                                        resumeOrderedStretch();
                                    }
                                }
                            },
                            helper: 'clone',
                        });
                    }

                    makeDraggable(jAfter, 'after');// вешаем на правую ручку группы хэндлер направления вправо
                    makeDraggable(jBefore, 'before');// вешаем на левую ручку группы хэндлер направления влево
                });

                jOrdered.each(function(i, el) {
                    $(el).popover({
                        delay: {
                            show: 500,
                            hide: 100
                        },
                        content: function() {
                            return $(this).find('.timemap__popover').html();
                        },
                        html: true,
                        trigger: 'hover',
                        placement: 'auto'
                    });
                });

                jFree.on('mousedown', function(e) {
                    if (e.which === 1) {
                        const self = $(this);
                        if (self.hasClass('free')) {
                            self.addClass('timemap__type--selected smart-selection__cell smart-selection__cell--start');
                            jContent.addClass('smart-selection--active');
                        }
                    }
                });

                jUpdated.removeClass('updated');
            });


            /**
             * Обработчик на движение мыши по страницы (выделение ячеек строки при зажатой клавише мыши)
             */
            if (!jBody.hasClass('smart-selection')) {
                jBody.addClass('smart-selection');
                jBody.off('mousemove.smart-selection');
                jBody.on('mousemove.smart-selection', function(e) {
                    if (jContent.hasClass('smart-selection--active')) {
                        const mouseX = e.pageX;
                        const jSelectionStart = jContent.find('.smart-selection__cell--start');
                        const width = jSelectionStart.outerWidth();
                        const offset = jSelectionStart.offset();
                        const fromX = offset.left;
                        const count = Math.abs((mouseX - fromX ) / width);
                        const direct = mouseX - fromX;
                        const jCell = $('.timemap__cell', jSelectionStart);
                        const jSiblings = getSiblings(jCell, direct > 0 ? 'after' : 'before');
                        jSelectionStart[direct < 0 ? 'nextAll' : 'prevAll']('.smart-selection__cell').removeClass('timemap__type--selected smart-selection__cell');
                        if (Math.floor(count) > 0) {
                            jSiblings.each(function(i, el) {
                                const g = $(el).closest('.timemap__group');
                                if (g.hasClass('free')) {
                                    g[i+(direct < 0 ? 0 : 1) > count ? 'removeClass' : 'addClass']('timemap__type--selected smart-selection__cell');
                                }
                            });
                        }
                    }
                });
                jBody.on('mouseup', function(e) {
                    if (jContent.hasClass('smart-selection--active')) {
                        const jSelectionCells = jContent.find('.smart-selection__cell');
                        const isSelectionStart = $(e.target).closest('.timemap__group').hasClass('smart-selection__cell--start');
                        const jCells = jSelectionCells.find('.timemap__cell');
                        jSelectionCells.removeClass('timemap__type--selected smart-selection__cell smart-selection__cell--start');
                        jContent.removeClass('smart-selection--active');
                        if (!isSelectionStart) {

                            const smartSelectionArr = jCells.toArray().map(function(el) {
                                return that.get_cell(el);
                            });

                            if (smartSelectionArr.length !== 1) {
                                that.select(smartSelectionArr);
                            }
                        }
                    }
                });
            }
        }
    });

    window.App = App;

    $(function() {

        if (_.filter([
                ['mutate', window],
                ['inputmask', $.fn],
                ['fancybox', $.fn],
                ['moment', window],
                ['daterangepicker', $.fn]
            ], function(item) { return typeof item[1][item[0]] === 'undefined'; }).length > 0) {
            return;
        }

        /**
         * Inputmask for phone inputs
         */
        const androidVersion = (function() {
            const ua = navigator.userAgent.toLowerCase();
            const match = ua.match(/android\s([0-9\.]*)/);
            return match ? match[1] : false;
        })();

        if (!navigator.userAgent.match(/Windows Phone/i)) {
            mutate('.inputmask-phone', function(elements) {

                $(elements).inputmask({
                    mask: parseInt(androidVersion, 10) < 6 ? '+7 (999)999-9999' : '+7 (999) 999-9999',
                    placeholder: ' '
                });

                $(elements).attr("placeholder", "+7 (   )    -    ");
            });
            mutate('.inputmask-money', function(elements) {
                $(elements).inputmask({ "mask": "9", "repeat": 12, "greedy": false });
            });
        }

        /**
         * Кнопка "выбрать дату"
         */
        $('.timemap-datepicker').on('apply.daterangepicker', function(e, picker) {
            app.date_goto(picker.startDate);
        });

        $('.timemap-datepicker-go').on('hide.daterangepicker', function(e, picker) {
            location.href = '?date='+picker.startDate.format('YYYY-MM-DD');
        });


        if (app && (app instanceof Vue)) {
            app.$watch('date', function(value) {
                const d = $('.timemap-datepicker').data('daterangepicker');
                if (d) {
                    d.setStartDate(this.date);
                    d.setEndDate(this.date);
                    d.updateView();
                }
            });
        }

        /**
         * fancybox
         */
        $('.fancybox').fancybox({
            title: false,
            scrolling: 'no'
        });

        /***
         * bootstrap datetimepicker
         */
        moment.locale('ru');

        mutate('.datepicker', function(elements) {

            $(elements).each(function(i, el) {

                const $el = $(el);
                const target_from = $el.attr('target-from');
                const target_to = $el.attr('target-to');
                const reload_selected = $el.attr('reload-selected');

                const options = {
                    showDropdowns: true,
                    locale: {
                        format: 'D MMM',
                        separator: ' - ',
                        applyLabel: 'Применить',
                        cancelLabel: 'Отменить',
                        fromLabel: 'С',
                        toLabel: 'По',
                        customRangeLabel: 'Custom',
                        weekLabel: 'нед.',
                        daysOfWeek: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
                        monthNames: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
                        firstDay: 1
                    }
                };

                $.each(['start', 'end', 'min', 'max'], function(key, item) {
                    const attributeName = `data-${item}-date`;
                    const attributeValue = $el.attr(attributeName);
                    if (attributeValue) {
                        options[item + 'Date'] = moment(attributeValue);
                    }
                });

                if (!options.startDate && target_from) {
                    options.startDate = moment($(target_from).val()) || moment().startOf('day');
                }

                if (!options.endDate && target_to) {
                    options.endDate = moment($(target_to).val()) || moment().endOf('day');
                }

                $el.daterangepicker(options);

                $el.on('apply.daterangepicker', function(e, picker) {
                    target_from && $(target_from).val(picker.startDate.format('YYYY-MM-DD'));
                    target_to && $(target_to).val(picker.endDate.format('YYYY-MM-DD'));
                });
            });
        });

        /**
         * bootstrap select
         */
        mutate('.selectpicker', function(elements) {
            $(elements).each(function(i, el) {
                $(el).selectpicker({
                    noneSelectedText: $(el).attr('placeholder') || ''
                });
            });
        });

    });

})(jQuery);
