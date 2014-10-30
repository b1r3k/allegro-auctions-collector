# -*- coding: UTF-8 -*-
'''
 * Author: Lukasz Jachym
 * Date: 11/2/13
 * Time: 2:03 PM
 *
 * This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
 * To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/.
'''
from collections import namedtuple

AllegroUser = namedtuple('AllegroUser', ['username', 'password', 'apikey'])

AllegroItem = namedtuple('AllegroItem', [   'unique_id', # unikalny hash tak aby ominac kolizje jesli allegro recycluje id
                                            'id',
                                            'bid_count', #Liczba ofert kupna złożonych w ofercie.
                                             'quantity_available', # Aktualna liczba przedmiotów dostępnych w ofercie.
                                             'quantity_sold', # liczba przedmiotów sprzedanych
                                             'seller_name',
                                             'seller_location', # miejscowosc / lokalizacja sprzedajacego
                                             'seller_rating', #Liczba punktów sprzedającego.
                                             # Liczba zdjęć dołączonych do oferty (dotyczy tylko tych wgranych na serwery Allegro).
                                             'foto_count',
                                             # Cena Kup Teraz! (jeżeli cena KT! nie jest ustawiona, w polu zwracane jest 0).
                                             'buy_now_price',
                                             'hit_count', # Liczba wyświetleń oferty.
                                             # Informacja na temat stanu oferty (1 - trwa, 2 - zakończyła się w sposób "naturalny" (koniec czasu trwania, albo wykupienie wszystkich dostępnych przedmiotów w przypadku Kup Teraz), 3 - została zakończona przez sprzedającego przed czasem).
                                             'ending_info',
                                             # Informacja o tym, czy oferta jest oznaczona jako Standard Allegro [PL], Aukro Plus [CZ] lub Super Offer [UA/KZ] (1 - jest, 0 - nie jest).
                                             'is_allegro_standard',
                                             # Informacja o stanie przedmiotu (0 - stan przedmiotu nie został ustalony, 1 - przedmiot jest nowy, 2 - przedmiot jest używany).
                                             'is_new',
                                             'title',
                                             'description',
                                             # czas zakonczenia oferty unix timestamp
                                             'ending_timestamp',
                                             # czas pobrania danych o itemie
                                             'fetched_timestamp',
])

def get_hash(id, timestamp):
    return int(id) + int(timestamp)

def get_item_hash(item):
    return get_hash(item.id, item.ending_timestamp)