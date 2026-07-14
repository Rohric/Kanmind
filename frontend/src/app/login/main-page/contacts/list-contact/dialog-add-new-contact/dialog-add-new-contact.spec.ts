import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DialogAddNewContact } from './dialog-add-new-contact';

describe('DialogAddNewContact', () => {
  let component: DialogAddNewContact;
  let fixture: ComponentFixture<DialogAddNewContact>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DialogAddNewContact]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DialogAddNewContact);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
